from mercadolab import Dinheiro


def test_dinheiro_ops():
    a = Dinheiro("USD", 100)
    b = Dinheiro("USD", 40)
    assert a.adicionar(b).valor == 140
    assert a.subtrair(b).valor == 60
