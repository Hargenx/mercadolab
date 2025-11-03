from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import Executor
from typing import Sequence, Callable, Dict, Tuple
from collections import deque
from itertools import repeat

from ... import Tempo, Ativo, Investidor, Transacao, Side

PriceFunc = Callable[[Ativo, Tempo], float]


# --- helpers top-level (evitam lambda; compatíveis com ProcessPool) ---
def _decidir_pair(pair: tuple[Investidor, Ativo], tempo: Tempo) -> Side:
    inv, ativo = pair
    return inv.decidir(ativo, tempo)


def _safe_hook(tx: Transacao) -> None:
    try:
        tx.trader.onTransacao(tx)
    except Exception:
        # TODO: log interno se quiser
        pass


@dataclass(slots=True)
class ParallelScheduler:
    executor: Executor
    price_fn: PriceFunc
    max_pair: int | None = None
    notify_hooks_in_parallel: bool = False  # deixe False por padrão (seguro)

    def run_tick(
        self,
        tempo: Tempo,
        ativos: Sequence[Ativo],
        investidores: Sequence[Investidor],
    ) -> list[Transacao]:
        # === 1) Decidir em paralelo com map (sem lambda) ===
        pairs: list[tuple[Investidor, Ativo]] = [
            (inv, ativo) for ativo in ativos for inv in investidores
        ]
        decisions = list(self.executor.map(_decidir_pair, pairs, repeat(tempo)))

        # === 2) Agrupar por ativo usando índices ===
        trades: list[Transacao] = []
        price_cache: Dict[str, float] = {}  # cache por ticker no tick
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

            n_pairs = min(len(buys), len(sells))
            if self.max_pair is not None:
                n_pairs = min(n_pairs, self.max_pair)
            if n_pairs == 0:
                continue

            ticker = ativo.ticker
            price = price_cache.get(ticker)
            if price is None:
                price = self.price_fn(ativo, tempo)
                price_cache[ticker] = price

            for i_pair in range(n_pairs):
                b_inv = buys.pop()
                s_inv = sells.pop()
                trades.append(
                    Transacao(
                        id=f"tx-{tempo.tick}-{ticker}-b{i_pair}",
                        trader=b_inv,
                        asset=ativo,
                        clock=tempo,
                        lado=Side.BUY,
                        preco=price,
                        quantidade=1,
                        ordemId="",
                    )
                )
                trades.append(
                    Transacao(
                        id=f"tx-{tempo.tick}-{ticker}-s{i_pair}",
                        trader=s_inv,
                        asset=ativo,
                        clock=tempo,
                        lado=Side.SELL,
                        preco=price,
                        quantidade=1,
                        ordemId="",
                    )
                )

        # === 3) Notificar hooks ===
        if not trades:
            return trades

        if self.notify_hooks_in_parallel:
            list(self.executor.map(_safe_hook, trades))
        else:
            for tx in trades:
                _safe_hook(tx)

        return trades

    def decide_only_tick(
        self,
        tempo: Tempo,
        ativos: Sequence[Ativo],
        investidores: Sequence[Investidor],
    ) -> Dict[str, Tuple[int, int]]:
        """Conta BUY/SELL por ativo, evitando criar Transacao (fast-path)."""
        pairs = [(inv, ativo) for ativo in ativos for inv in investidores]
        decisions = list(self.executor.map(_decidir_pair, pairs, repeat(tempo)))
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
