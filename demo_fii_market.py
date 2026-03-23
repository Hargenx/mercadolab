from mercadolab.scenarios import FIIMarketConfig, FIIMarketScenario


def main() -> None:
    config = FIIMarketConfig(
        num_dias=30,
        num_investidores=30,
        ticker_fii="MXRF11",
        seed=42,
    )

    cenario = FIIMarketScenario(config=config)
    resultado = cenario.executar()

    print("=" * 60)
    print("RESUMO GERAL")
    print("=" * 60)
    print("Dias executados:", resultado.dias_executados)
    print("Número de investidores:", len(resultado.investidores))
    print("Número total de transações:", len(resultado.transacoes))
    print("Número de dividendos registrados:", len(resultado.historico_dividendos))
    dividendos_nao_zero = [d for d in resultado.historico_dividendos if d > 0]
    print("Dividendos não zero:", dividendos_nao_zero)
    print("Soma dos dividendos registrados:", sum(resultado.historico_dividendos))
    print("Dividendos (amostra):", resultado.historico_dividendos[:10])
    print("Caixa final do FII:", resultado.fii.caixa)
    print("Valor patrimonial por cota final:", resultado.fii.valor_patrimonial_por_cota())
    print("Preço inicial:", resultado.historico_precos[0])
    print("Preços (amostra):", resultado.historico_precos[:10])
    print("Preço final:", resultado.historico_precos[-1])
    print(
        "Último dividendo:",
        resultado.historico_dividendos[-1] if resultado.historico_dividendos else 0.0,
    )


if __name__ == "__main__":
    main()
