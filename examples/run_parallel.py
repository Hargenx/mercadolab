from concurrent.futures import Executor
from mercadolab import Dinheiro, Tempo, Ativo, Mercado, Side
from mercadolab import Investidor, Fundamentalista, Especulativo, Ruido
from mercadolab.internal.engine import make_executor, ParallelScheduler


class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo) -> float:
    return 100.0 + 0.1 * tempo.tick


def main() -> None:
    ativos = [Ativo("AAA11"), Ativo("BBB3")]
    investidores: list[Investidor] = [
        Buyer("i1", "Raphael", Dinheiro("BRL", 1000)),
        Buyer("i2", "Gilson", Dinheiro("BRL", 800)),
        Seller("i3", "Sara", Dinheiro("BRL", 500)),
    ]
    tempo = Tempo(1)

    with make_executor("thread", max_workers=8) as ex:  # "process" se CPU-bound
        sched = ParallelScheduler(executor=ex, price_fn=price_fn, max_pair=10)
        txs = sched.run_tick(tempo, ativos, investidores)
        for t in txs:
            print(t)


if __name__ == "__main__":
    main()
