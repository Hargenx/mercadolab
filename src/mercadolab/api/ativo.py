from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Ativo:
    """<<kind>> — entidade negociavel."""

    ticker: str

    def id(self) -> str:
        return self.ticker
