from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tempo:
    """Representa um instante discreto de tempo na simulação."""

    tick: int

    def __post_init__(self) -> None:
        if self.tick < 0:
            raise ValueError("O tick não pode ser negativo.")

    def proximo(self) -> "Tempo":
        return Tempo(self.tick + 1)
