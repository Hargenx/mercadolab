from decimal import Decimal

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import LadoOrdem, TipoOrdem
from mercadolab.api.posicao import Posicao
from mercadolab.api.simulacao import Simulacao
from mercadolab.api.tempo import Tempo


def test_simulacao_executa_tick_e_avanca_tempo() -> None:
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
        quantidade=5,
        preco_medio=Decimal("95.00"),
    )

    simulacao = Simulacao(
        mercado=mercado,
        tempo_atual=Tempo(tick=0),
    )
    simulacao.adicionar_investidor(comprador)
    simulacao.adicionar_investidor(vendedor)

    ordem_venda = vendedor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=simulacao.tempo_atual,
        preco_limite=Decimal("100.00"),
    )
    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=simulacao.tempo_atual,
        preco_limite=Decimal("100.00"),
    )

    transacoes = simulacao.executar_tick([ordem_venda, ordem_compra])

    assert len(transacoes) == 1
    assert simulacao.tempo_atual.tick == 1
