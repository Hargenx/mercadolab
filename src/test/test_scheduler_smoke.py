# tests/test_scheduler_smoke.py
from mercadolab import Dinheiro, Tempo, Ativo, Side
from mercadolab import Fundamentalista, Especulativo, Investidor
from mercadolab.internal.engine import make_executor, ParallelScheduler


# Investidores determinísticos
class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(_: Ativo, tempo: Tempo) -> float:
    return 100.0 + 0.1 * tempo.tick  # determinístico


def test_parallel_scheduler_thread():
    ativos = [Ativo("AAA11"), Ativo("BBB3")]
    investidores: list[Investidor] = [
        Buyer("i1", "Raphael", Dinheiro("BRL", 1000)),
        Seller("i2", "Juliana", Dinheiro("BRL", 800)),
    ]
    tempo = Tempo(1)

    with make_executor("thread", max_workers=4) as ex:
        sched = ParallelScheduler(executor=ex, price_fn=price_fn)
        trades = sched.run_tick(tempo, ativos, investidores)

    # 2 ativos x (BUY+SELL pareados) = 2 transações por ativo = 4 no total
    assert len(trades) == 4
    assert all(t.preco == price_fn(t.asset, tempo) for t in trades)
    # cada trade referencia o mesmo tick/tempo
    assert {t.clock.tick for t in trades} == {tempo.tick}
