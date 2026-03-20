# tests/test_scheduler_mercado_fallback.py
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from mercadolab.api.enums import Side
from mercadolab.api.ativo import Ativo
from mercadolab.api.tempo import Tempo
from mercadolab.api.dinheiro import Dinheiro
from mercadolab.api.investidor import Investidor
from mercadolab.internal.engine.scheduler import ParallelScheduler


class Buyer(Investidor):
    def decidir(self, ativo, tempo):
        return Side.BUY


class Seller(Investidor):
    def decidir(self, ativo, tempo):
        return Side.SELL


def test_scheduler_uses_price_fn_when_mercado_is_none():
    ativos = [Ativo("BBB3")]
    tempo = Tempo(1)
    buyer = Buyer("b", "Buyer", Dinheiro("BRL", 1e9))
    seller = Seller("s", "Seller", Dinheiro("BRL", 0.0))

    def price_fn(a, t):
        return 123.45

    with ThreadPoolExecutor(max_workers=2) as ex:
        sched = ParallelScheduler(executor=ex, price_fn=price_fn, enforce_cash=True)
        trades = sched.run_tick(tempo, ativos, [buyer, seller])

    assert len(trades) == 2
    assert trades[0].preco == 123.45
    assert trades[1].preco == 123.45
