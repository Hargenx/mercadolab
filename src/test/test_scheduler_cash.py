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


def preco_fixo(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
    """Retorna preço fixo para os testes de caixa."""
    return 100.0


def test_compra_sem_saldo_e_bloqueada_quando_enforce_cash_true() -> None:
    mercado = Mercado("mercado_teste")
    mercado.adicionar_ativo(Ativo("AAA11"))

    comprador = Comprador("b1", "Comprador", Dinheiro("BRL", 0.0))
    vendedor = Vendedor("s1", "Vendedor", Dinheiro("BRL", 0.0))
    tempo = Tempo(1)

    with ThreadPoolExecutor(max_workers=4) as executor:
        scheduler = ParallelScheduler(
            mercado=mercado,
            investidores=(comprador, vendedor),
            executor=executor,
        )
        transacoes = scheduler.executar_passo(
            tempo,
            price_fn=preco_fixo,
            enforce_cash=True,
        )

    assert len(transacoes) == 0


def test_compra_com_saldo_transfere_caixa_corretamente() -> None:
    mercado = Mercado("mercado_teste")
    mercado.adicionar_ativo(Ativo("AAA11"))

    comprador = Comprador("b1", "Comprador", Dinheiro("BRL", 100.0))
    vendedor = Vendedor("s1", "Vendedor", Dinheiro("BRL", 0.0))
    tempo = Tempo(1)

    with ThreadPoolExecutor(max_workers=2) as executor:
        scheduler = ParallelScheduler(
            mercado=mercado,
            investidores=(comprador, vendedor),
            executor=executor,
        )
        transacoes = scheduler.executar_passo(
            tempo,
            price_fn=preco_fixo,
            enforce_cash=True,
        )

    # 1 ativo x 1 comprador x 1 vendedor = 2 transações (compra e venda)
    assert len(transacoes) == 2
    assert abs(comprador.carteira.valor - 0.0) < 1e-9
    assert abs(vendedor.carteira.valor - 100.0) < 1e-9
