from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo
from mercadolab.internal.engine import ParallelScheduler, make_executor


class AgenteCompradorContextual(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        if ativo.ticker == "AAA11":
            return Side.BUY
        if ativo.ticker == "BBB3":
            return Side.BUY if tempo.tick % 2 == 0 else Side.SELL
        return Side.SELL


class AgenteVendedorContextual(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        if ativo.ticker == "AAA11":
            return Side.SELL
        if ativo.ticker == "BBB3":
            return Side.SELL if tempo.tick % 2 == 0 else Side.BUY
        return Side.BUY


def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
    base = 100.0 + (tempo.tick - 1)

    ajuste_ativo = {
        "AAA11": 0.0,
        "BBB3": 5.0,
        "CCC4": 10.0,
    }.get(ativo.ticker, 0.0)

    ajuste_mercado = len(mercado.listar_ativos()) * 0.1
    return base + ajuste_ativo + ajuste_mercado


def main() -> None:
    mercado = Mercado("mercado_demo")
    mercado.adicionar_ativo(Ativo("AAA11"))
    mercado.adicionar_ativo(Ativo("BBB3"))
    mercado.adicionar_ativo(Ativo("CCC4"))

    investidores = (
        AgenteCompradorContextual(
            "c1", "Comprador 1", Dinheiro("BRL", 10_000.0), perfil="comprador"
        ),
        AgenteCompradorContextual(
            "c2", "Comprador 2", Dinheiro("BRL", 10_000.0), perfil="comprador"
        ),
        AgenteVendedorContextual(
            "v1", "Vendedor 1", Dinheiro("BRL", 10_000.0), perfil="vendedor"
        ),
        AgenteVendedorContextual(
            "v2", "Vendedor 2", Dinheiro("BRL", 10_000.0), perfil="vendedor"
        ),
    )

    with make_executor(max_workers=4) as executor:
        scheduler = ParallelScheduler(
            mercado=mercado,
            investidores=investidores,
            executor=executor,
        )

        for tick in range(1, 7):
            tempo = Tempo(tick)
            transacoes = scheduler.executar_passo(
                tempo,
                price_fn=price_fn,
                enforce_cash=True,
            )

            print(f"\n{'=' * 60}")
            print(f"TICK {tick}")
            print(f"{'=' * 60}")
            print(f"Transações executadas: {len(transacoes)}")

            if not transacoes:
                print("Nenhuma transação executada neste tick.")
                continue

            for tx in transacoes[:6]:
                print(
                    f"{tx.id} | ativo={tx.ativo.ticker} | lado={tx.lado} | "
                    f"preço={tx.preco:.2f} | quantidade={tx.quantidade}"
                )


if __name__ == "__main__":
    main()
