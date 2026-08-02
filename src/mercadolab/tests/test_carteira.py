from decimal import Decimal

import pytest

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira


def test_carteira_aplica_compra_e_venda() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )
    carteira = Carteira(caixa=Decimal("1000.00"))

    carteira.aplicar_compra(ativo=ativo, quantidade=5, preco=Decimal("100.00"))
    posicao = carteira.obter_posicao(ativo)

    assert posicao is not None
    assert carteira.caixa == Decimal("500.00")
    assert posicao.quantidade == 5
    assert posicao.preco_medio == Decimal("100.00")

    carteira.aplicar_venda(ativo=ativo, quantidade=2, preco=Decimal("110.00"))
    posicao = carteira.obter_posicao(ativo)

    assert posicao is not None
    assert carteira.caixa == Decimal("720.00")
    assert posicao.quantidade == 3

def test_carteira_nao_cria_posicao_quando_compra_eh_invalida() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=10,
    )
    carteira = Carteira(caixa=Decimal("1000.00"))

    with pytest.raises(ValueError, match="quantidade inválida"):
        carteira.aplicar_compra(
            ativo=ativo,
            quantidade=1,
            preco=Decimal("100.00"),
        )

    assert carteira.caixa == Decimal("1000.00")
    assert carteira.obter_posicao(ativo) is None
    assert carteira.posicoes == {}