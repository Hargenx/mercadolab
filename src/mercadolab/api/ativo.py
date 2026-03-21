from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Ativo:
    """Representa um ativo negociável em um cenário de mercado."""

    ticker: str
