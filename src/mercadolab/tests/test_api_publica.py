import mercadolab

SIMBOLOS_PUBLICOS = {
    "Ativo",
    "Carteira",
    "Investidor",
    "LadoOrdem",
    "LivroDeOfertas",
    "Mercado",
    "Ordem",
    "Posicao",
    "Simulacao",
    "StatusOrdem",
    "Tempo",
    "TipoAtivo",
    "TipoOrdem",
    "Transacao",
}


def test_api_publica_exporta_componentes_atuais() -> None:
    assert set(mercadolab.__all__) == SIMBOLOS_PUBLICOS

    for nome in SIMBOLOS_PUBLICOS:
        assert hasattr(mercadolab, nome)