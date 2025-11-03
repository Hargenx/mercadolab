from mercadolab import Dinheiro, Tempo, Ativo, Side
from mercadolab import Fundamentalista, Especulativo, Investidor
from mercadolab.internal.engine import make_executor, ParallelScheduler


# Investidores determinísticos p/ demo
class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo) -> float:
    # Preço determinístico simples
    return 100.0 + 0.25 * tempo.tick


def main() -> None:
    ativos = [Ativo("AAA11"), Ativo("BBB3")]
    investidores: list[Investidor] = [
        Buyer("i1", "Raphael", Dinheiro("BRL", 1000)),
        Seller("i2", "Gilson", Dinheiro("BRL", 800)),
        Buyer("i3", "Vinicius", Dinheiro("BRL", 1200)),
        Seller("i4", "Sara", Dinheiro("BRL", 700)),
    ]
    tempo = Tempo(1)

    with make_executor("thread", max_workers=8) as ex:
        sched = ParallelScheduler(executor=ex, price_fn=price_fn, max_pair=None)
        trades = sched.run_tick(tempo, ativos, investidores)

    for t in trades:
        print(
            f"{t.id} | {t.asset.ticker} | {t.lado} | {t.preco:.2f} | qty={t.quantidade}"
        )


if __name__ == "__main__":
    main()
