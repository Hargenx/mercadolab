from __future__ import annotations
from mercadolab import (
    Dinheiro,
    Tempo,
    Ativo,
    Side,
    Fundamentalista,
    Especulativo,
    Investidor,
)
from mercadolab.internal.engine import make_executor, ParallelScheduler
from concurrent.futures import as_completed


# Agentes simples
class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def decide_excess_parallel(
    executor, investidores: list[Investidor], ativo: Ativo, tempo: Tempo
) -> int:
    """Conta decisões BUY-SELL em paralelo (modelo do Colab)."""
    futures = [executor.submit(inv.decidir, ativo, tempo) for inv in investidores]
    buys = sells = 0
    for fut in as_completed(futures):
        side = fut.result()
        if side is Side.BUY:
            buys += 1
        elif side is Side.SELL:
            sells += 1
    return buys - sells  # excess = BUY - SELL


def main():
    ativos = [Ativo("AAA11")]
    investidores: list[Investidor] = []
    for i in range(60):  # MAIS compradores
        investidores.append(Buyer(f"b{i}", f"Buyer{i}", Dinheiro("BRL", 0)))
    for j in range(40):  # MENOS vendedores
        investidores.append(Seller(f"s{j}", f"Seller{j}", Dinheiro("BRL", 0)))

    preco = 100.0
    k = 0.1
    ticks = 20

    with make_executor("thread", max_workers=32) as ex:
        # scheduler opcional: gera trades para fins de inspeção/log
        sched = ParallelScheduler(
            executor=ex, price_fn=lambda a, t: preco, max_pair=None
        )

        for t in range(1, ticks + 1):
            tempo = Tempo(t)

            # 1) EXCESSO DE DEMANDA (decisões), como no Colab
            excess = decide_excess_parallel(ex, investidores, ativos[0], tempo)

            # 2) Atualiza preço pelo excesso (modelo Colab)
            preco = preco + k * excess

            # 3) (Opcional) gerar trades só para observar pareamentos
            trades = sched.run_tick(tempo, ativos, investidores)

            print(
                f"t={t:02d}  trades={len(trades):3d}  excess={excess:+4d}  price={preco:.2f}"
            )


if __name__ == "__main__":
    main()
