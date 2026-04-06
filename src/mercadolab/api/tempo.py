from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Tempo:
    """Representa um instante discreto de tempo na simulação."""

    tick: int
    timestamp: datetime | None = None
    sessao: str | None = None

    def __post_init__(self) -> None:
        if self.tick < 0:
            raise ValueError("O tick não pode ser negativo.")

    def proximo(self) -> "Tempo":
        """Retorna o próximo instante discreto da mesma sessão."""
        return Tempo(self.tick + 1, sessao=self.sessao)
