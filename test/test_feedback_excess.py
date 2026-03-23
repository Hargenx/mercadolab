from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo
from mercadolab.internal.engine import ParallelScheduler, make_executor


class Comprador(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Vendedor(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def run_feedback(n_buy: int, n_sell: int, ticks: int = 10, k: float = 0.1) -> float:
    mercado = Mercado("mercado_feedback")
    ativo = Ativo("AAA11")
    mercado.adicionar_ativo(ativo)

    investidores: tuple[Investidor, ...] = tuple(
        Comprador(f"b{i}", f"Buyer{i}", Dinheiro("BRL", 1_000_000.0))
        for i in range(n_buy)
    ) + tuple(
        Vendedor(f"s{j}", f"Seller{j}", Dinheiro("BRL", 0.0)) for j in range(n_sell)
    )

    preco_atual = 100.0

    def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
        return preco_atual

    with make_executor(max_workers=32) as executor:
        scheduler = ParallelScheduler(
            mercado=mercado,
            investidores=investidores,
            executor=executor,
        )

        for tick in range(1, ticks + 1):
            tempo = Tempo(tick)

            excesso = sum(
                1 for inv in investidores if inv.decidir(ativo, tempo) is Side.BUY
            ) - sum(1 for inv in investidores if inv.decidir(ativo, tempo) is Side.SELL)

            preco_atual = preco_atual + k * excesso
            _ = scheduler.executar_passo(
                tempo,
                price_fn=price_fn,
                enforce_cash=False,
            )

    return preco_atual


def test_price_goes_up_when_more_buyers() -> None:
    assert run_feedback(n_buy=60, n_sell=40, ticks=10) > 100.0


def test_price_goes_down_when_more_sellers() -> None:
    assert run_feedback(n_buy=40, n_sell=60, ticks=10) < 100.0


def test_price_stays_flat_when_balanced() -> None:
    assert abs(run_feedback(n_buy=50, n_sell=50, ticks=10) - 100.0) < 1e-9
