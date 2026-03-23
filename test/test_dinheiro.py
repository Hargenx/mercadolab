import pytest
from mercadolab import Dinheiro


def test_dinheiro_rejeita_operacao_com_moedas_diferentes() -> None:
    a = Dinheiro("USD", 100)
    b = Dinheiro("BRL", 40)

    with pytest.raises(ValueError, match="mesma moeda"):
        a.adicionar(b)


def test_dinheiro_rejeita_subtracao_com_saldo_insuficiente() -> None:
    a = Dinheiro("USD", 10)
    b = Dinheiro("USD", 40)

    with pytest.raises(ValueError, match="Saldo insuficiente"):
        a.subtrair(b)
