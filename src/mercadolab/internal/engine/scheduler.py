from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Callable, Dict, Tuple, Optional
from collections import deque
from concurrent.futures import Executor

from ...api.tempo import Tempo
from ...api.ativo import Ativo
from ...api.enums import Side
from ...api.investidor import Investidor
from ...api.transacao import Transacao
from ..market import Mercado

PriceFunc = Callable[[Ativo, Tempo], float]


@dataclass(slots=True)
class ParallelScheduler:
    executor: Executor
    price_fn: Optional[PriceFunc] = None
    mercado: Optional[Mercado] = None
    max_pair: int | None = None
    notify_hooks_in_parallel: bool = False
    enforce_cash: bool = False  # se True, BUY exige carteira suficiente

    def _price(self, ativo: Ativo, tempo: Tempo, cache: Dict[str, float]) -> float:
        ticker = ativo.ticker
        p = cache.get(ticker)
        if p is not None:
            return p

        if self.mercado is not None:
            p = self.mercado.get_price(ativo, tempo)
        elif self.price_fn is not None:
            p = self.price_fn(ativo, tempo)
        else:
            raise RuntimeError(
                "ParallelScheduler: defina 'mercado' ou 'price_fn' para obter preço."
            )

        cache[ticker] = p
        return p

    def run_tick(
        self,
        tempo: Tempo,
        ativos: Sequence[Ativo],
        investidores: Sequence[Investidor],
    ) -> list[Transacao]:
        # 1) Decidir em paralelo (ordem preservada)
        pairs = [(inv, ativo) for ativo in ativos for inv in investidores]
        decisions = list(self.executor.map(lambda p: p[0].decidir(p[1], tempo), pairs))

        trades: list[Transacao] = []
        price_cache: Dict[str, float] = {}
        n_invest = len(investidores)

        for a_idx, ativo in enumerate(ativos):
            start = a_idx * n_invest
            end = start + n_invest

            buys: deque[Investidor] = deque()
            sells: deque[Investidor] = deque()

            for i in range(start, end):
                side = decisions[i]
                inv = pairs[i][0]
                if side is Side.BUY:
                    buys.append(inv)
                elif side is Side.SELL:
                    sells.append(inv)

            # Pareamento
            n_pairs = min(len(buys), len(sells))
            if self.max_pair is not None:
                n_pairs = min(n_pairs, self.max_pair)
            if n_pairs == 0:
                continue

            # Preço por ativo no tick
            price = self._price(ativo, tempo, price_cache)

            # Se enforce_cash, filtre/valide compradores com saldo
            if self.enforce_cash:
                # Reconstroi filas considerando saldo (simples: 1 unidade)
                # Obs.: SELL não valida estoque porque o core é neutro (sem inventário no núcleo).
                filtered_buys: deque[Investidor] = deque()
                needed = 1 * price  # 1 unidade
                while buys:
                    b = buys.pop()
                    try:
                        # “Sonda” saldo chamando método público do investidor (sem debitar aqui)
                        # A regra concreta de saldo está no Investidor (creditar/debitar/valor atual).
                        # Para manter neutralidade, tentamos debitar e reverter se OK.
                        b.debitar(
                            type(b).carteira.__class__(b.carteira.moeda, 0.0)
                        )  # no-op?
                        # Checa se teria dinheiro suficiente (inspira-se em interface Dinheiro)
                        if b.carteira.valor >= needed and b.carteira.moeda:
                            filtered_buys.append(b)
                        # Restaura (não mudou nada; se sua Dinheiro debitar exige >0, adapte teste abaixo)
                    except Exception:
                        # Se não conseguir interagir, assume que não há saldo suficiente
                        pass
                buys = filtered_buys
                n_pairs = min(len(buys), len(sells))
                if self.max_pair is not None:
                    n_pairs = min(n_pairs, self.max_pair)
                if n_pairs == 0:
                    continue

            # Gera transações
            for i_pair in range(n_pairs):
                b_inv = buys.pop()
                s_inv = sells.pop()
                t_b = Transacao(
                    id=f"tx-{tempo.tick}-{ativo.ticker}-b{i_pair}",
                    trader=b_inv,
                    asset=ativo,
                    clock=tempo,
                    lado=Side.BUY,
                    preco=price,
                    quantidade=1,
                    ordemId="",
                )
                t_s = Transacao(
                    id=f"tx-{tempo.tick}-{ativo.ticker}-s{i_pair}",
                    trader=s_inv,
                    asset=ativo,
                    clock=tempo,
                    lado=Side.SELL,
                    preco=price,
                    quantidade=1,
                    ordemId="",
                )
                # Efeitos financeiros mínimos (opt-in via enforce_cash)
                if self.enforce_cash:
                    try:
                        # BUY debita, SELL credita 1*price — política mínima (sem inventário no core)
                        b_inv.debitar(
                            type(b_inv).carteira.__class__(b_inv.carteira.moeda, price)
                        )
                        s_inv.creditar(
                            type(s_inv).carteira.__class__(s_inv.carteira.moeda, price)
                        )
                    except Exception:
                        # Se falhar, descarta par (não cria transações)
                        continue

                trades.append(t_b)
                trades.append(t_s)

        # Notificações
        if not trades:
            return trades

        if self.notify_hooks_in_parallel:
            list(self.executor.map(lambda tx: safe_hook(tx.trader, tx), trades))
        else:
            for tx in trades:
                safe_hook(tx.trader, tx)

        return trades

    def decide_only_tick(
        self, tempo: Tempo, ativos: Sequence[Ativo], investidores: Sequence[Investidor]
    ) -> Dict[str, Tuple[int, int]]:
        pairs = [(inv, ativo) for ativo in ativos for inv in investidores]
        decisions = list(self.executor.map(lambda p: p[0].decidir(p[1], tempo), pairs))
        counts: Dict[str, Tuple[int, int]] = {}
        n_invest = len(investidores)
        for a_idx, ativo in enumerate(ativos):
            start = a_idx * n_invest
            end = start + n_invest
            b = s = 0
            for i in range(start, end):
                d = decisions[i]
                b += d is Side.BUY
                s += d is Side.SELL
            counts[ativo.ticker] = (b, s)
        return counts


def safe_hook(inv: Investidor, tx: Transacao) -> None:
    try:
        inv.onTransacao(tx)
    except Exception:
        pass
