from __future__ import annotations
from dataclasses import dataclass
from concurrent.futures import Executor, as_completed
from typing import Sequence, Callable, Dict, List, Tuple

# >>> use a API pública do pacote (mercadolab.__init__ reexporta a UML)
from ... import Tempo, Ativo, Investidor, Transacao, Side

PriceFunc = Callable[[Ativo, Tempo], float]


@dataclass(slots=True)
class ParallelScheduler:
    """
    Orquestra um 'tick' chamando decidir() dos investidores em paralelo.
    Não altera a API pública (UML). Resultado: lista de Transacao.
    """

    executor: Executor
    price_fn: PriceFunc
    max_pair: int | None = None  # limite de pareamentos por ativo (opcional)

    def run_tick(
        self,
        tempo: Tempo,
        ativos: Sequence[Ativo],
        investidores: Sequence[Investidor],
    ) -> list[Transacao]:
        # 1) Decidir em paralelo
        futures: Dict[object, Tuple[Investidor, Ativo]] = {}
        for ativo in ativos:
            for inv in investidores:
                fut = self.executor.submit(inv.decidir, ativo, tempo)
                futures[fut] = (inv, ativo)

        decisions: Dict[Ativo, List[Tuple[Investidor, Side]]] = {a: [] for a in ativos}
        for fut in as_completed(futures):
            inv, ativo = futures[fut]
            side = fut.result()  # se exceção, propaga (útil p/ debug)
            if side in (Side.BUY, Side.SELL):
                decisions[ativo].append((inv, side))

        # 2) Parear decisões e gerar Transacao
        trades: list[Transacao] = []
        for ativo, votes in decisions.items():
            buys = [x for x in votes if x[1] is Side.BUY]
            sells = [x for x in votes if x[1] is Side.SELL]
            n = min(len(buys), len(sells))
            if self.max_pair is not None:
                n = min(n, self.max_pair)
            if n == 0:
                continue
            price = self.price_fn(ativo, tempo)
            for i in range(n):
                b_inv = buys[i][0]
                s_inv = sells[i][0]
                # duas Transacao: perspectiva de cada trader
                trades.append(
                    Transacao(
                        id=f"tx-{tempo.tick}-{ativo.ticker}-b{i}",
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
                        id=f"tx-{tempo.tick}-{ativo.ticker}-s{i}",
                        trader=s_inv,
                        asset=ativo,
                        clock=tempo,
                        lado=Side.SELL,
                        preco=price,
                        quantidade=1,
                        ordemId="",
                    )
                )

        # 3) Notificar hooks (em série para evitar data races)
        for tx in trades:
            try:
                tx.trader.onTransacao(tx)
            except Exception:
                # log opcional aqui
                pass

        return trades
