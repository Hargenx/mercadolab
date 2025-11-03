from __future__ import annotations
import pandas as pd
from mercadolab import Dinheiro, Tempo, Ativo, Side
from mercadolab import Fundamentalista, Especulativo, Investidor
from mercadolab.internal.engine import make_executor, ParallelScheduler

# --- CONFIG ---
CSV_PATH = "examples/prices_example.csv"  # tick,ticker,price


# Investidores determinísticos p/ parear compras/vendas
class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def build_price_fn_from_csv(csv_path: str):
    df = pd.read_csv(csv_path)  # colunas: tick(int), ticker(str), price(float)
    df["tick"] = df["tick"].astype(int)
    # índice multi para lookup rápido
    df = df.set_index(["ticker", "tick"]).sort_index()

    def price_fn(ativo: Ativo, tempo: Tempo) -> float:
        try:
            return float(df.loc[(ativo.ticker, tempo.tick), "price"])
        except KeyError as exc:
            raise KeyError(
                f"Preco nao encontrado para ticker={ativo.ticker} tick={tempo.tick}"
            ) from exc

    return price_fn


def main() -> None:
    ativos = [Ativo("AAA11"), Ativo("BBB3")]
    investidores: list[Investidor] = [
        Buyer("i1", "Raphael", Dinheiro("BRL", 1000)),
        Seller("i2", "Gilson", Dinheiro("BRL", 800)),
    ]
    tempo = Tempo(1)

    price_fn = build_price_fn_from_csv(CSV_PATH)

    with make_executor("thread", max_workers=4) as ex:
        sched = ParallelScheduler(executor=ex, price_fn=price_fn, max_pair=None)
        trades = sched.run_tick(tempo, ativos, investidores)

    for t in trades:
        print(
            f"{t.id} | {t.asset.ticker} | {t.lado} | {t.preco:.2f} | qty={t.quantidade}"
        )


if __name__ == "__main__":
    main()
