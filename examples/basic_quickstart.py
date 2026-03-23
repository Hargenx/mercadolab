from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo
from mercadolab.internal.engine import ParallelScheduler, make_executor


class Buyer(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
    return 100.0


mercado = Mercado("mercado_teste")
mercado.adicionar_ativo(Ativo("AAA11"))

investidores = (
    Buyer("b1", "Buyer 1", Dinheiro("BRL", 1000.0)),
    Seller("s1", "Seller 1", Dinheiro("BRL", 1000.0)),
)

with make_executor(max_workers=8) as executor:
    scheduler = ParallelScheduler(
        mercado=mercado,
        investidores=investidores,
        executor=executor,
    )
    transacoes = scheduler.executar_passo(
        Tempo(1),
        price_fn=price_fn,
        enforce_cash=True,
    )

print(transacoes)
