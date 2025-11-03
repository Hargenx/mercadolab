from mercadolab import (
    Dinheiro,
    Investidor,
    Fundamentalista,
    Ativo,
    Tempo,
    Transacao,
    Side,
)


class Dummy(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


def test_transacao_event():
    inv = Dummy("i1", "Alice", Dinheiro("USD", 1000))
    ativo = Ativo("ABCD3")
    t = Tempo(1)
    tx = Transacao("tx1", inv, ativo, t, Side.BUY, 10.0, 5, "ord1")
    assert tx.isBuy()
    assert tx.notional() == 50.0
