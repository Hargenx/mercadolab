from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from mercadolab.api.ativo import Ativo
from mercadolab.api.dinheiro import Dinheiro
from mercadolab.api.enums import Side
from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.tempo import Tempo
from mercadolab.internal.engine.scheduler import ParallelScheduler


class Comprador(Investidor):
    """Investidor determinístico que sempre decide comprar."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Vendedor(Investidor):
    """Investidor determinístico que sempre decide vender."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def test_scheduler_usa_price_fn_fornecida() -> None:
    mercado = Mercado("mercado_teste")
    mercado.adicionar_ativo(Ativo("BBB3"))

    tempo = Tempo(1)
    comprador = Comprador("b", "Buyer", Dinheiro("BRL", 1e9))
    vendedor = Vendedor("s", "Seller", Dinheiro("BRL", 0.0))

    def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
        return 123.45

    with ThreadPoolExecutor(max_workers=2) as executor:
        scheduler = ParallelScheduler(
            mercado=mercado,
            investidores=(comprador, vendedor),
            executor=executor,
        )
        transacoes = scheduler.executar_passo(
            tempo,
            price_fn=price_fn,
            enforce_cash=True,
        )

    assert len(transacoes) == 2
    assert transacoes[0].preco == 123.45
    assert transacoes[1].preco == 123.45
