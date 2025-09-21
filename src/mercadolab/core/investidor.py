from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from mercadolab.core.world import MundoBase

@dataclass
class Order:
    id: int
    agent: "InvestidorBase"
    side: str  # "buy" or "sell"
    qty: float

    def reset(self, ambiente: "MundoBase") -> None:
        pass

    def agir(self, ambiente: "MundoBase") -> None:
        """Cada investidor decide e registra ordens no ambiente."""
        raise NotImplementedError

@dataclass
class InvestidorBase:
    name: str
    cash: float = 1000.0
    holdings: Dict[str, float] = field(default_factory=lambda: {"ASSET": 0.0})
    state: Dict[str, Any] = field(default_factory=dict)

    def decide(self, market) -> Optional[Order]:
        """Retorna uma ordem ou None. Deve ser sobrescrito pelos agentes concretos."""
        return None

    def on_fill(self, side: str, qty: float, price: float) -> None:
        if side == "buy":
            self.cash -= qty * price
            self.holdings["ASSET"] = self.holdings.get("ASSET", 0.0) + qty
        elif side == "sell":
            self.cash += qty * price
            self.holdings["ASSET"] = self.holdings.get("ASSET", 0.0) - qty
