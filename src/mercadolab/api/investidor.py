from __future__ import annotations  # <- evita avaliar hints em runtime
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .dinheiro import Dinheiro
from .ativo import Ativo
from .tempo import Tempo
from .enums import Side

if TYPE_CHECKING:  # <- só para editores/mypy; não roda em runtime
    from .transacao import Transacao


@dataclass(slots=True)
class Investidor:
    """
    <<role>> — agente do framework. Subtipos refletem a UML.
    """

    id: str
    nome: str
    carteira: Dinheiro
    carreira: str = ""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:  # abstract na UML
        raise NotImplementedError("Subclasses devem implementar decidir().")

    def onTransacao(
        self, trans: Transacao
    ) -> None:  # hint funciona por causa do TYPE_CHECKING
        """Hook para reagir a execucoes."""
        return None

    def creditar(self, valor: Dinheiro) -> None:
        if not self.carteira.igualMoeda(valor):
            raise ValueError("Moedas diferentes")
        self.carteira = self.carteira.adicionar(valor)

    def debitar(self, valor: Dinheiro) -> None:
        if not self.carteira.igualMoeda(valor):
            raise ValueError("Moedas diferentes")
        self.carteira = self.carteira.subtrair(valor)


class Fundamentalista(Investidor):
    pass


class Especulativo(Investidor):
    pass


class Ruido(Investidor):
    pass
