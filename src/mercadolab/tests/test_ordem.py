from decimal import Decimal

import pytest

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.ordem import LadoOrdem, Ordem, StatusOrdem, TipoOrdem
from mercadolab.api.tempo import Tempo


def criar_contexto() -> tuple[Ativo, Investidor, Tempo]:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )
    investidor = Investidor(
        nome="Alice",
        carteira=Carteira(caixa=Decimal("1000.00")),
    )
    tempo = Tempo(tick=0)
    return ativo, investidor, tempo


def test_ordem_limitada_exige_preco_limite() -> None:
    ativo, investidor, tempo = criar_contexto()

    with pytest.raises(ValueError):
        Ordem(
            ativo=ativo,
            investidor=investidor,
            lado=LadoOrdem.COMPRA,
            tipo=TipoOrdem.LIMITADA,
            quantidade=1,
            tempo=tempo,
            preco_limite=None,
        )


def test_ordem_registra_execucao_parcial_e_total() -> None:
    ativo, investidor, tempo = criar_contexto()

    ordem = Ordem(
        ativo=ativo,
        investidor=investidor,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=tempo,
        preco_limite=Decimal("100.00"),
    )

    ordem.registrar_execucao(2)
    assert ordem.quantidade_restante == 3
    assert ordem.status is StatusOrdem.PARCIALMENTE_EXECUTADA

    ordem.registrar_execucao(3)
    assert ordem.quantidade_restante == 0
    assert ordem.status is StatusOrdem.EXECUTADA
