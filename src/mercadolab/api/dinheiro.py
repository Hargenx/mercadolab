from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Dinheiro:
    """Objeto de valor que representa uma quantia monetária em uma moeda."""

    moeda: str
    valor: float

    def adicionar(self, outro: "Dinheiro") -> "Dinheiro":
        self._validar_mesma_moeda(outro)
        return Dinheiro(self.moeda, self.valor + outro.valor)

    def subtrair(self, outro: "Dinheiro") -> "Dinheiro":
        self._validar_mesma_moeda(outro)
        novo_valor = self.valor - outro.valor
        if novo_valor < 0:
            raise ValueError("Saldo insuficiente para realizar a operação.")
        return Dinheiro(self.moeda, novo_valor)

    def mesma_moeda(self, outro: "Dinheiro") -> bool:
        return self.moeda == outro.moeda

    def _validar_mesma_moeda(self, outro: "Dinheiro") -> None:
        if not self.mesma_moeda(outro):
            raise ValueError("A operação requer valores na mesma moeda.")
