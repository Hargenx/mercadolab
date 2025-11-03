from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Dinheiro:
    """<<quantity>> — valor monetario em uma moeda."""

    moeda: str
    valor: float

    # Métodos utilitários da UML
    def adicionar(self, outro: "Dinheiro") -> "Dinheiro":
        self._igual_moeda(outro)
        return Dinheiro(self.moeda, self.valor + outro.valor)

    def subtrair(self, outro: "Dinheiro") -> "Dinheiro":
        self._igual_moeda(outro)
        novo = self.valor - outro.valor
        if novo < 0:
            raise ValueError("Saldo insuficiente")
        return Dinheiro(self.moeda, novo)

    def igualMoeda(self, outro: "Dinheiro") -> bool:  # nome igual ao da UML
        return self.moeda == outro.moeda

    def _igual_moeda(self, outro: "Dinheiro") -> None:
        if not self.igualMoeda(outro):
            raise ValueError("Moedas diferentes")
