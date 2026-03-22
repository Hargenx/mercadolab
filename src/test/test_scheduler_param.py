import pytest

from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo
from mercadolab.internal.engine import ParallelScheduler, make_executor


class Comprador(Investidor):
    """Investidor determinístico que sempre decide comprar."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Vendedor(Investidor):
    """Investidor determinístico que sempre decide vender."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
    """Função de preço determinística usada no teste parametrizado."""
    return 100.0 + tempo.tick


@pytest.mark.parametrize("max_workers", [1, 2])
def test_scheduler_parametrizado(max_workers: int) -> None:
    mercado = Mercado("mercado_teste")
    mercado.adicionar_ativo(Ativo("AAA11"))

    investidores: tuple[Investidor, ...] = (
        Comprador("i1", "Raphael", Dinheiro("BRL", 1000)),
        Vendedor("i2", "Caroline", Dinheiro("BRL", 800)),
    )
    tempo = Tempo(1)

    with make_executor(max_workers=max_workers) as executor:
        scheduler = ParallelScheduler(
            mercado=mercado,
            investidores=investidores,
            executor=executor,
        )
        transacoes = scheduler.executar_passo(tempo, price_fn=price_fn)

    assert len(transacoes) == 2  # 1 compra + 1 venda => 2 transações
    assert all(t.preco == 101.0 for t in transacoes)
    assert {t.tempo.tick for t in transacoes} == {1}
