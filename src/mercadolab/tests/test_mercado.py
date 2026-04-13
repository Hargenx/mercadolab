from decimal import Decimal

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import LadoOrdem, TipoOrdem
from mercadolab.api.posicao import Posicao
from mercadolab.api.tempo import Tempo


def test_mercado_submete_ordens_e_gera_transacao() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )

    mercado = Mercado(nome="Mercado Teste")
    mercado.adicionar_ativo(ativo)

    comprador = Investidor(
        nome="Comprador",
        carteira=Carteira(caixa=Decimal("1000.00")),
    )
    vendedor = Investidor(
        nome="Vendedor",
        carteira=Carteira(caixa=Decimal("0.00")),
    )
    vendedor.carteira.posicoes[ativo.ticker] = Posicao(
        ativo=ativo,
        quantidade=10,
        preco_medio=Decimal("90.00"),
    )

    tempo = Tempo(tick=0)

    ordem_venda = vendedor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=tempo,
        preco_limite=Decimal("100.00"),
    )
    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=tempo,
        preco_limite=Decimal("100.00"),
    )

    mercado.submeter_ordem(ordem_venda)
    transacoes = mercado.submeter_ordem(ordem_compra)

    assert len(transacoes) == 1
    assert transacoes[0].quantidade == 5
    assert transacoes[0].preco == Decimal("100.00")
    assert comprador.carteira.caixa == Decimal("500.00")
    assert vendedor.carteira.caixa == Decimal("500.00")
