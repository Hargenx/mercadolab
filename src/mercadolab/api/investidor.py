from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .ativo import Ativo
from .dinheiro import Dinheiro
from .enums import Side
from .tempo import Tempo

if TYPE_CHECKING:
    from .transacao import Transacao


@dataclass(slots=True)
class Investidor(ABC):
    """
    Agente base do framework para cenários de mercado.

    Subclasses devem implementar a lógica de decisão do investidor.
    """

    id: str
    nome: str
    carteira: Dinheiro
    perfil: str = ""

    @abstractmethod
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        """
        Retorna a ação do investidor para um ativo em um dado instante.
        """
        ...

    def on_transacao(self, transacao: Transacao) -> None:
        """
        Hook executado após uma transação envolvendo o investidor.
        """
        pass

    def creditar(self, valor: Dinheiro) -> None:
        self._validar_mesma_moeda(valor)
        self.carteira = self.carteira.adicionar(valor)

    def debitar(self, valor: Dinheiro) -> None:
        self._validar_mesma_moeda(valor)
        self.carteira = self.carteira.subtrair(valor)

    def _validar_mesma_moeda(self, valor: Dinheiro) -> None:
        if not self.carteira.mesma_moeda(valor):
            raise ValueError("A operação requer valores na mesma moeda.")
