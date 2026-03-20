from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from mercadolab.api.enums import Side
from mercadolab.api.ativo import Ativo
from mercadolab.api.tempo import Tempo
from mercadolab.api.dinheiro import Dinheiro
from mercadolab.api.investidor import Investidor
from mercadolab.internal.engine.scheduler import ParallelScheduler
from mercadolab.internal.market import SimpleMercado


class Buyer(Investidor):
    def decidir(self, ativo, tempo):
        return Side.BUY


class Seller(Investidor):
    def decidir(self, ativo, tempo):
        return Side.SELL


def test_buy_without_cash_is_blocked_when_enforce_cash_true():
    ativos = [Ativo("AAA11")]
    # Buyer sem saldo suficiente
    buyer = Buyer("b1", "Buyer", Dinheiro("BRL", 0.0))
    seller = Seller("s1", "Seller", Dinheiro("BRL", 0.0))
    tempo = Tempo(1)

    def p(ativo, t):  # preço fixo = 100
        return 100.0

    with ThreadPoolExecutor(max_workers=4) as ex:
        sched = ParallelScheduler(
            executor=ex,
            mercado=SimpleMercado(price_fn=p),
            enforce_cash=True,
        )
        trades = sched.run_tick(tempo, ativos, [buyer, seller])

    # Sem cash suficiente, não deve cruzar
    assert len(trades) == 0


def test_buy_with_cash_succeeds_and_transfers_cash():
    ativos = [Ativo("AAA11")]
    # Buyer com 100, Seller com 0 — 1 unidade a 100
    buyer = Buyer("b1", "Buyer", Dinheiro("BRL", 100.0))
    seller = Seller("s1", "Seller", Dinheiro("BRL", 0.0))
    tempo = Tempo(1)

    def p(ativo, t):  # preço fixo = 100
        return 100.0

    with ThreadPoolExecutor(max_workers=2) as ex:
        sched = ParallelScheduler(
            executor=ex,
            mercado=SimpleMercado(price_fn=p),
            enforce_cash=True,
        )
        trades = sched.run_tick(tempo, ativos, [buyer, seller])

    # Deve ter 2 transações (buy/sell)
    assert len(trades) == 2
    # Buyer debita 100, Seller credita 100
    assert abs(buyer.carteira.valor - 0.0) < 1e-9
    assert abs(seller.carteira.valor - 100.0) < 1e-9
