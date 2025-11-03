from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tempo:
    """Marcador temporal da simulacao."""

    tick: int

    # Métodos sugeridos na UML
    def atual(self) -> int:
        return self.tick

    def proximo(self) -> "Tempo":
        return Tempo(self.tick + 1)
