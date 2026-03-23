# tests/test_bench_decidir.py
import pytest
from src.mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo
from src.mercadolab.internal.engine import ParallelScheduler, make_executor


class Comprador(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Vendedor(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
    return 100.0


@pytest.mark.benchmark(group="scheduler-tick")
def test_scheduler_tick_benchmark(benchmark) -> None:
    mercado = Mercado("mercado_bench")
    for ticker in ("AAA11", "BBB3", "CCC4"):
        mercado.adicionar_ativo(Ativo(ticker))

    investidores: tuple[Investidor, ...] = tuple(
        Comprador(f"b{i}", f"B{i}", Dinheiro("BRL", 1000.0)) for i in range(500)
    ) + tuple(Vendedor(f"s{j}", f"S{j}", Dinheiro("BRL", 0.0)) for j in range(500))

    tempo = Tempo(1)

    def run() -> None:
        with make_executor(max_workers=32) as executor:
            scheduler = ParallelScheduler(
                mercado=mercado,
                investidores=investidores,
                executor=executor,
            )
            _ = scheduler.executar_passo(
                tempo,
                price_fn=price_fn,
                enforce_cash=False,
            )

    benchmark(run)
