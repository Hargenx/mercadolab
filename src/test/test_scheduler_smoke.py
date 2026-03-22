from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo
from mercadolab.internal.engine import ParallelScheduler, make_executor


class Comprador(Investidor):
    """Investidor determinístico que sempre decide comprar."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Vendedor(Investidor):
    """Investidor determinístico que sempre decide vender."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
    """Função de preço determinística para testes."""
    return 100.0 + 0.1 * tempo.tick


def test_parallel_scheduler_thread() -> None:
    mercado = Mercado("mercado_teste")
    mercado.adicionar_ativo(Ativo("AAA11"))
    mercado.adicionar_ativo(Ativo("BBB3"))

    investidores: list[Investidor] = [
        Comprador("i1", "Raphael", Dinheiro("BRL", 1000)),
        Vendedor("i2", "Juliana", Dinheiro("BRL", 800)),
    ]
    tempo = Tempo(1)

    with make_executor(max_workers=4) as executor:
        scheduler = ParallelScheduler(
            mercado=mercado,
            investidores=tuple(investidores),
            executor=executor,
        )
        transacoes = scheduler.executar_passo(tempo, price_fn=price_fn)

    # 2 ativos x (1 comprador + 1 vendedor) = 2 transações por ativo = 4 no total
    assert len(transacoes) == 4
    assert all(t.preco == price_fn(t.ativo, tempo, mercado) for t in transacoes)
    assert {t.tempo.tick for t in transacoes} == {tempo.tick}
