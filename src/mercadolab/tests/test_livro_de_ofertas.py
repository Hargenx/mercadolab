from decimal import Decimal

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.livro_de_ofertas import LivroDeOfertas
from mercadolab.api.ordem import LadoOrdem, Ordem, TipoOrdem
from mercadolab.api.tempo import Tempo


def criar_ordem(
    investidor_nome: str,
    preco: str,
    tick: int,
) -> Ordem:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )
    investidor = Investidor(
        nome=investidor_nome,
        carteira=Carteira(caixa=Decimal("10000.00")),
    )
    return Ordem(
        ativo=ativo,
        investidor=investidor,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=1,
        tempo=Tempo(tick=tick),
        preco_limite=Decimal(preco),
    )


def test_livro_prioriza_preco_e_tempo_na_compra() -> None:
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )
    livro = LivroDeOfertas(ativo=ativo)

    ordem1 = criar_ordem("A", "100.00", 1)
    ordem2 = criar_ordem("B", "101.00", 2)
    ordem3 = criar_ordem("C", "101.00", 0)

    livro.adicionar_ordem(ordem1)
    livro.adicionar_ordem(ordem2)
    livro.adicionar_ordem(ordem3)

    melhor = livro.melhor_compra()
    assert melhor is not None
    assert melhor.investidor.nome == "C"
