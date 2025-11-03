# tests/test_bench_decidir.py
import pytest
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


class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


@pytest.mark.benchmark(group="tick")
def test_tick_benchmark(benchmark):
    ativos = [Ativo("AAA11"), Ativo("BBB3"), Ativo("CCC4")]
    investidores: list[Investidor] = [
        Buyer(f"b{i}", f"B{i}", Dinheiro("BRL", 0)) for i in range(500)
    ] + [Seller(f"s{j}", f"S{j}", Dinheiro("BRL", 0)) for j in range(500)]
    tempo = Tempo(1)

    def run():
        with make_executor("thread", max_workers=32) as ex:
            sched = ParallelScheduler(ex, price_fn=lambda a, t: 100.0, max_pair=None)
            _ = sched.run_tick(tempo, ativos, investidores)

    benchmark(run)
