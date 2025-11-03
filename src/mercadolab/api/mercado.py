from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple
from .ativo import Ativo


@dataclass(slots=True)
class Mercado:
    """<<collective>> — compoe Ativos (UML: Mercado *-- Ativo)."""

    nome: str
    _ativos: Dict[str, Ativo] = field(default_factory=dict, repr=False)

    def adicionarAtivo(self, ativo: Ativo) -> None:
        if ativo.ticker in self._ativos:
            raise ValueError("Ativo ja existente")
        self._ativos[ativo.ticker] = ativo

    def removerAtivo(self, ticker: str) -> None:
        self._ativos.pop(ticker)

    def obterAtivo(self, ticker: str) -> Ativo:
        return self._ativos[ticker]

    def listarAtivos(self) -> Tuple[Ativo, ...]:
        return tuple(self._ativos.values())
