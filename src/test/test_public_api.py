import mercadolab as ml


def test_public_api_matches_uml_surface():
    assert set(ml.__all__) == {
        "Side",
        "Dinheiro",
        "Tempo",
        "Ativo",
        "Mercado",
        "Investidor",
        "Fundamentalista",
        "Especulativo",
        "Ruido",
        "Transacao",
    }
