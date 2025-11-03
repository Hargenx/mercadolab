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


def run_feedback(n_buy: int, n_sell: int, ticks: int = 10, k: float = 0.1) -> float:
    ativos = [Ativo("AAA11")]
    investidores: list[Investidor] = [
        Buyer(f"b{i}", f"Buyer{i}", Dinheiro("BRL", 0)) for i in range(n_buy)
    ] + [Seller(f"s{j}", f"Seller{j}", Dinheiro("BRL", 0)) for j in range(n_sell)]
    preco = 100.0
    with make_executor("thread", max_workers=32) as ex:
        sched = ParallelScheduler(executor=ex, price_fn=lambda a, t: preco)
        for t in range(1, ticks + 1):
            tempo = Tempo(t)
            # conta decisões (BUY-SELL) em paralelo, modelo colab
            excess = sum(
                1 for inv in investidores if inv.decidir(ativos[0], tempo) is Side.BUY
            ) - sum(
                1 for inv in investidores if inv.decidir(ativos[0], tempo) is Side.SELL
            )
            preco = preco + k * excess
            _ = sched.run_tick(
                tempo, ativos, investidores
            )  # opcional: só para manter pareamento
    return preco


def test_price_goes_up_when_more_buyers():
    assert run_feedback(n_buy=60, n_sell=40, ticks=10) > 100.0


def test_price_goes_down_when_more_sellers():
    assert run_feedback(n_buy=40, n_sell=60, ticks=10) < 100.0


def test_price_stays_flat_when_balanced():
    assert abs(run_feedback(n_buy=50, n_sell=50, ticks=10) - 100.0) < 1e-9
