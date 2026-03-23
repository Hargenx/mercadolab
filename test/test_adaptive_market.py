from mercadolab.scenarios import AdaptiveMarketConfig, AdaptiveMarketScenario


def test_adaptive_market_executa_e_gera_transacoes() -> None:
    config = AdaptiveMarketConfig(
        n_agentes=20,
        ativos=("AAA11", "BBB3"),
        ticks=10,
        saldo_inicial=100_000.0,
        preco_inicial=100.0,
        tamanho_vizinhanca=5,
        peso_vizinhos=0.5,
        peso_carteira=0.3,
        peso_externo=0.2,
        max_workers=4,
    )

    cenario = AdaptiveMarketScenario(config=config)
    resultado = cenario.executar()

    assert resultado.ticks_executados == 10
    assert len(resultado.investidores) == 20
    assert len(resultado.mercado.listar_ativos()) == 2
    assert len(resultado.transacoes) > 0
    assert len(resultado.sinais_externos) == 10


def test_adaptive_market_produz_heterogeneidade_de_saldos() -> None:
    config = AdaptiveMarketConfig(
        n_agentes=20,
        ativos=("AAA11",),
        ticks=10,
        saldo_inicial=100_000.0,
        preco_inicial=100.0,
        tamanho_vizinhanca=5,
        peso_vizinhos=0.5,
        peso_carteira=0.3,
        peso_externo=0.2,
        max_workers=4,
    )

    cenario = AdaptiveMarketScenario(config=config)
    resultado = cenario.executar()

    saldos = {investidor.carteira.valor for investidor in resultado.investidores}

    assert len(saldos) > 1


def test_adaptive_market_registra_transacoes_para_ativos_do_cenario() -> None:
    config = AdaptiveMarketConfig(
        n_agentes=20,
        ativos=("AAA11", "BBB3", "CCC4"),
        ticks=5,
        saldo_inicial=100_000.0,
        preco_inicial=100.0,
        tamanho_vizinhanca=5,
        peso_vizinhos=0.5,
        peso_carteira=0.3,
        peso_externo=0.2,
        max_workers=4,
    )

    cenario = AdaptiveMarketScenario(config=config)
    resultado = cenario.executar()

    ativos_esperados = {"AAA11", "BBB3", "CCC4"}
    ativos_observados = {tx.ativo.ticker for tx in resultado.transacoes}

    assert ativos_observados.issubset(ativos_esperados)
    assert len(ativos_observados) > 0
