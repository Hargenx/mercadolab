from mercadolab import Dinheiro, Investidor, Ativo, Tempo, Transacao, Side


class Dummy(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


def test_transacao_evento() -> None:
    investidor = Dummy("i1", "Alice", Dinheiro("USD", 1000))
    ativo = Ativo("ABCD3")
    tempo = Tempo(1)

    tx = Transacao(
        id="tx1",
        investidor=investidor,
        ativo=ativo,
        tempo=tempo,
        lado=Side.BUY,
        preco=10.0,
        quantidade=5,
        ordem_id="ord1",
    )

    assert tx.eh_compra()
    assert not tx.eh_venda()
    assert tx.valor_total() == 50.0
