from decimal import Decimal

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import LadoOrdem, StatusOrdem, TipoOrdem
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

    posicao_comprador = comprador.carteira.obter_posicao(ativo)
    posicao_vendedor = vendedor.carteira.obter_posicao(ativo)

    assert posicao_comprador is not None
    assert posicao_comprador.quantidade == 5
    assert posicao_comprador.preco_medio == Decimal("100.00")

    assert posicao_vendedor is not None
    assert posicao_vendedor.quantidade == 5
    assert posicao_vendedor.preco_medio == Decimal("90.00")

def test_mercado_cancela_ordem_e_remove_do_livro() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )
    mercado = Mercado(nome="Mercado Teste")
    mercado.adicionar_ativo(ativo)

    investidor = Investidor(
        nome="Comprador",
        carteira=Carteira(caixa=Decimal("1000.00")),
    )
    ordem = investidor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("100.00"),
    )

    mercado.submeter_ordem(ordem)
    livro = mercado.obter_livro(ativo.ticker)

    assert livro.melhor_compra() is ordem

    mercado.cancelar_ordem(ordem)

    assert ordem.status is StatusOrdem.CANCELADA
    assert livro.melhor_compra() is None

def test_mercado_descarta_ordem_cancelada_encontrada_no_livro() -> None:
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
        preco_medio=Decimal("90.00"),
    )

    ordem_venda = vendedor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("100.00"),
    )
    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=1),
        preco_limite=Decimal("100.00"),
    )

    mercado.submeter_ordem(ordem_venda)
    ordem_venda.cancelar()

    transacoes = mercado.submeter_ordem(ordem_compra)
    livro = mercado.obter_livro(ativo.ticker)

    assert transacoes == ()
    assert ordem_venda.status is StatusOrdem.CANCELADA
    assert livro.melhor_venda() is None
    assert livro.melhor_compra() is ordem_compra

def test_ordem_sem_cobertura_nao_remove_contraparte_valida() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )
    mercado = Mercado(nome="Mercado Teste")
    mercado.adicionar_ativo(ativo)

    comprador = Investidor(
        nome="Comprador sem cobertura",
        carteira=Carteira(caixa=Decimal("0.00")),
    )
    vendedor = Investidor(
        nome="Vendedor válido",
        carteira=Carteira(caixa=Decimal("0.00")),
    )
    vendedor.carteira.posicoes[ativo.ticker] = Posicao(
        ativo=ativo,
        quantidade=5,
        preco_medio=Decimal("90.00"),
    )

    ordem_venda = vendedor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("100.00"),
    )
    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=1),
        preco_limite=Decimal("100.00"),
    )

    mercado.submeter_ordem(ordem_venda)
    transacoes = mercado.submeter_ordem(ordem_compra)

    livro = mercado.obter_livro(ativo.ticker)
    posicao_vendedor = vendedor.carteira.obter_posicao(ativo)

    assert transacoes == ()
    assert livro.melhor_venda() is ordem_venda
    assert ordem_venda.esta_ativa()
    assert ordem_venda.quantidade_executada == 0
    assert posicao_vendedor is not None
    assert posicao_vendedor.quantidade == 5

def test_mercado_expira_contraparte_sem_cobertura_removida_do_livro() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )
    mercado = Mercado(nome="Mercado Teste")
    mercado.adicionar_ativo(ativo)

    comprador = Investidor(
        nome="Comprador sem cobertura",
        carteira=Carteira(caixa=Decimal("0.00")),
    )
    vendedor = Investidor(
        nome="Vendedor válido",
        carteira=Carteira(caixa=Decimal("0.00")),
    )
    vendedor.carteira.posicoes[ativo.ticker] = Posicao(
        ativo=ativo,
        quantidade=5,
        preco_medio=Decimal("90.00"),
    )

    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("100.00"),
    )
    ordem_venda = vendedor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=1),
        preco_limite=Decimal("100.00"),
    )

    mercado.submeter_ordem(ordem_compra)
    transacoes = mercado.submeter_ordem(ordem_venda)

    livro = mercado.obter_livro(ativo.ticker)

    assert transacoes == ()
    assert ordem_compra.status is StatusOrdem.EXPIRADA
    assert ordem_compra not in livro.listar_ordens_compra()
    assert livro.melhor_venda() is ordem_venda

def test_mercado_executa_compra_contra_multiplas_vendas() -> None:
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
    vendedor_1 = Investidor(nome="Vendedor 1")
    vendedor_2 = Investidor(nome="Vendedor 2")

    vendedor_1.carteira.posicoes[ativo.ticker] = Posicao(
        ativo=ativo,
        quantidade=3,
        preco_medio=Decimal("90.00"),
    )
    vendedor_2.carteira.posicoes[ativo.ticker] = Posicao(
        ativo=ativo,
        quantidade=4,
        preco_medio=Decimal("90.00"),
    )

    ordem_venda_1 = vendedor_1.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=3,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("100.00"),
    )
    ordem_venda_2 = vendedor_2.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=4,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("101.00"),
    )
    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=1),
        preco_limite=Decimal("101.00"),
    )

    mercado.submeter_ordem(ordem_venda_2)
    mercado.submeter_ordem(ordem_venda_1)
    transacoes = mercado.submeter_ordem(ordem_compra)

    assert [(t.quantidade, t.preco) for t in transacoes] == [
        (3, Decimal("100.00")),
        (2, Decimal("101.00")),
    ]
    assert ordem_compra.status is StatusOrdem.EXECUTADA
    assert ordem_venda_1.status is StatusOrdem.EXECUTADA
    assert ordem_venda_2.status is StatusOrdem.PARCIALMENTE_EXECUTADA
    assert ordem_venda_2.quantidade_restante == 2

    assert comprador.carteira.caixa == Decimal("498.00")
    assert vendedor_1.carteira.caixa == Decimal("300.00")
    assert vendedor_2.carteira.caixa == Decimal("202.00")

    posicao_comprador = comprador.carteira.obter_posicao(ativo)
    posicao_vendedor_2 = vendedor_2.carteira.obter_posicao(ativo)

    assert posicao_comprador is not None
    assert posicao_comprador.quantidade == 5
    assert posicao_comprador.preco_medio == Decimal("100.40")
    assert vendedor_1.carteira.obter_posicao(ativo) is None
    assert posicao_vendedor_2 is not None
    assert posicao_vendedor_2.quantidade == 2
    assert posicao_vendedor_2.preco_medio == Decimal("90.00")

    livro = mercado.obter_livro(ativo.ticker)
    assert livro.melhor_venda() is ordem_venda_2

def test_ordem_a_mercado_executa_disponivel_e_expira_saldo() -> None:
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
    vendedor = Investidor(nome="Vendedor")
    vendedor.carteira.posicoes[ativo.ticker] = Posicao(
        ativo=ativo,
        quantidade=3,
        preco_medio=Decimal("90.00"),
    )

    ordem_venda = vendedor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=3,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("100.00"),
    )
    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.MERCADO,
        quantidade=5,
        tempo=Tempo(tick=1),
    )

    mercado.submeter_ordem(ordem_venda)
    transacoes = mercado.submeter_ordem(ordem_compra)

    assert len(transacoes) == 1
    assert transacoes[0].quantidade == 3
    assert transacoes[0].preco == Decimal("100.00")

    assert ordem_venda.status is StatusOrdem.EXECUTADA
    assert ordem_compra.status is StatusOrdem.EXPIRADA
    assert ordem_compra.quantidade_executada == 3
    assert ordem_compra.quantidade_restante == 2

    livro = mercado.obter_livro(ativo.ticker)
    assert livro.melhor_compra() is None
    assert livro.melhor_venda() is None

    posicao_comprador = comprador.carteira.obter_posicao(ativo)
    assert comprador.carteira.caixa == Decimal("700.00")
    assert vendedor.carteira.caixa == Decimal("300.00")
    assert posicao_comprador is not None
    assert posicao_comprador.quantidade == 3
    assert vendedor.carteira.obter_posicao(ativo) is None

def test_mercado_nao_executa_ordens_com_precos_incompativeis() -> None:
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
    vendedor = Investidor(nome="Vendedor")
    vendedor.carteira.posicoes[ativo.ticker] = Posicao(
        ativo=ativo,
        quantidade=5,
        preco_medio=Decimal("90.00"),
    )

    ordem_venda = vendedor.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=0),
        preco_limite=Decimal("101.00"),
    )
    ordem_compra = comprador.emitir_ordem(
        ativo=ativo,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=Tempo(tick=1),
        preco_limite=Decimal("100.00"),
    )

    mercado.submeter_ordem(ordem_venda)
    transacoes = mercado.submeter_ordem(ordem_compra)

    livro = mercado.obter_livro(ativo.ticker)

    assert transacoes == ()
    assert livro.melhor_compra() is ordem_compra
    assert livro.melhor_venda() is ordem_venda
    assert ordem_compra.status is StatusOrdem.PENDENTE
    assert ordem_venda.status is StatusOrdem.PENDENTE
    assert comprador.carteira.caixa == Decimal("1000.00")
    assert vendedor.carteira.caixa == Decimal("0.00")

    posicao_vendedor = vendedor.carteira.obter_posicao(ativo)
    assert posicao_vendedor is not None
    assert posicao_vendedor.quantidade == 5