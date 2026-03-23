from collections import Counter
from mercadolab import Ativo, Tempo
from mercadolab.scenarios import AdaptiveMarketConfig, AdaptiveMarketScenario


def main() -> None:
    config = AdaptiveMarketConfig(
        n_agentes=100,
        ativos=("AAA11", "BBB3", "CCC4"),
        ticks=30,
        saldo_inicial=100_000.0,
        preco_inicial=100.0,
        tamanho_vizinhanca=5,
        peso_vizinhos=0.5,
        peso_carteira=0.3,
        peso_externo=0.2,
        max_workers=8,
    )

    cenario = AdaptiveMarketScenario(config=config)

    investidores = cenario.criar_investidores()


    for inv in investidores[:6]:
        print(inv.id, getattr(inv, "vies_pessoal", None))

    ativo = Ativo("AAA11")
    tempo = Tempo(1)

    for inv in investidores[:6]:
        inv.sinal_externo_atual = 1.0
        print(inv.id, inv.decidir(ativo, tempo))

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

    print("\n" + "=" * 60)
    print("TRANSAÇÕES POR ATIVO")
    print("=" * 60)
    for ticker, total in sorted(transacoes_por_ativo.items()):
        print(f"{ticker}: {total}")

    print("\n" + "=" * 60)
    print("TRANSAÇÕES POR TICK")
    print("=" * 60)
    for tick, total in sorted(transacoes_por_tick.items()):
        print(f"Tick {tick:03d}: {total}")

    print("\n" + "=" * 60)
    print("SINAIS EXTERNOS")
    print("=" * 60)
    for i, sinal in enumerate(resultado.sinais_externos, start=1):
        print(f"Tick {i:03d}: {sinal:+.1f}")

    print("\n" + "=" * 60)
    print("AMOSTRA DE INVESTIDORES")
    print("=" * 60)
    for investidor in resultado.investidores[:5]:
        print(
            f"{investidor.id} | {investidor.nome} | "
            f"perfil={investidor.perfil} | "
            f"saldo={investidor.carteira.moeda} {investidor.carteira.valor:.2f}"
        )


if __name__ == "__main__":
    main()
