import pytest
from mercadolab import Dinheiro, Tempo, Ativo, Side, Fundamentalista, Especulativo
from mercadolab.internal.engine import make_executor, ParallelScheduler


class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo) -> float:
    return 100.0 + tempo.tick


@pytest.mark.parametrize("mode", ["thread", "process"])
def test_scheduler(mode):
    ativos = [Ativo("AAA11")]
    investidores = [
        Buyer("i1", "Raphael", Dinheiro("BRL", 1000)),
        Seller("i2", "Caroline", Dinheiro("BRL", 800)),
    ]
    tempo = Tempo(1)

    with make_executor(mode, max_workers=2) as ex:
        sched = ParallelScheduler(executor=ex, price_fn=price_fn)
        trades = sched.run_tick(tempo, ativos, investidores)

    assert len(trades) == 2  # 1 buy + 1 sell => 2 Transacao (uma por lado)
    assert all(t.preco == 101.0 for t in trades)
    assert {t.clock.tick for t in trades} == {1}
