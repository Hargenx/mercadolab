from decimal import Decimal

import pytest

from mercadolab.api.ativo import Ativo, TipoAtivo


def test_ativo_valida_quantidade_e_preco() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )

    assert ativo.validar_quantidade(10)
    assert not ativo.validar_quantidade(0)
    assert ativo.validar_preco(Decimal("100.00"))
    assert not ativo.validar_preco(Decimal("100.005"))


def test_ativo_nao_aceita_ticker_vazio() -> None:
    with pytest.raises(ValueError):
        Ativo(
            ticker="",
            tipo=TipoAtivo.FII,
        )
