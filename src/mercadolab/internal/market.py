from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Callable

from ..api.tempo import Tempo
from ..api.ativo import Ativo


class Mercado(Protocol):
    """Contrato mínimo de mercado injetável no Scheduler."""

    def get_price(self, ativo: Ativo, tempo: Tempo) -> float: ...


@dataclass(slots=True)
class SimpleMercado:
    """Mercado mínimo com função de preço injetada (fallback ao price_fn antigo)."""

    price_fn: Callable[[Ativo, Tempo], float]

    def get_price(self, ativo: Ativo, tempo: Tempo) -> float:
        return self.price_fn(ativo, tempo)
