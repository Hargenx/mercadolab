from collections import Counter, defaultdict

from mercadolab.scenarios import BasicMarketScenario


def main() -> None:
    cenario = BasicMarketScenario(
        n_compradores=50,
        n_vendedores=50,
        ativos=("AAA11", "BBB3", "CCC4"),
        ticks=100,
        saldo_inicial_comprador=1_000_000.0,
        saldo_inicial_vendedor=0.0,
        preco_inicial=100.0,
        max_workers=8,
    )

    resultado = cenario.executar()

    print("=" * 60)
    print("RESUMO GERAL")
    print("=" * 60)
    print("Ticks executados:", resultado.ticks_executados)
    print("Número de investidores:", len(resultado.investidores))
    print("Número de ativos:", len(resultado.mercado.listar_ativos()))
    print("Número total de transações:", len(resultado.transacoes))

    transacoes_por_ativo = Counter(tx.ativo.ticker for tx in resultado.transacoes)
    transacoes_por_tick = Counter(tx.tempo.tick for tx in resultado.transacoes)

    volume_financeiro_por_ativo = defaultdict(float)
    preco_medio_por_tick = defaultdict(list)

    for tx in resultado.transacoes:
        volume_financeiro_por_ativo[tx.ativo.ticker] += tx.valor_total()
        preco_medio_por_tick[tx.tempo.tick].append(tx.preco)

    print("\n" + "=" * 60)
    print("TRANSAÇÕES POR ATIVO")
    print("=" * 60)
    for ticker, total in sorted(transacoes_por_ativo.items()):
        print(f"{ticker}: {total}")

    print("\n" + "=" * 60)
    print("VOLUME FINANCEIRO POR ATIVO")
    print("=" * 60)
    for ticker, volume in sorted(volume_financeiro_por_ativo.items()):
        print(f"{ticker}: {volume:.2f}")

    print("\n" + "=" * 60)
    print("PREÇO MÉDIO POR TICK")
    print("=" * 60)
    for tick in sorted(preco_medio_por_tick):
        media = sum(preco_medio_por_tick[tick]) / len(preco_medio_por_tick[tick])
        print(f"Tick {tick:03d}: {media:.2f}")

    print("\n" + "=" * 60)
    print("AMOSTRA DE INVESTIDORES")
    print("=" * 60)
    for investidor in resultado.investidores[:5]:
        print(
            f"{investidor.id} | {investidor.nome} | "
            f"perfil={investidor.perfil} | "
            f"saldo={investidor.carteira.moeda} {investidor.carteira.valor:.2f}"
        )

    print("\n" + "=" * 60)
    print("CHECAGENS")
    print("=" * 60)

    esperado_por_tick = (
        len(resultado.mercado.listar_ativos())
        * min(cenario.n_compradores, cenario.n_vendedores)
        * 2
    )
    esperado_total = esperado_por_tick * cenario.ticks

    print("Transações esperadas por tick:", esperado_por_tick)
    print("Transações esperadas no total:", esperado_total)
    print("Transações observadas:", len(resultado.transacoes))
    print("Consistente?", esperado_total == len(resultado.transacoes))


if __name__ == "__main__":
    main()
