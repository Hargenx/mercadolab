from __future__ import annotations
import random
from dataclasses import dataclass
from ..core.investidor import BaseAgent, Order

@dataclass
class RandomTrader(BaseAgent):
    max_qty: float = 1.0
    p_trade: float = 0.5
    seed: int = 123

    def __post_init__(self):
        self._rng = random.Random(self.seed)

    def decide(self, market):
        if self._rng.random() < self.p_trade:
            side = "buy" if self._rng.random() < 0.5 else "sell"
            qty = self._rng.uniform(0.1, self.max_qty)
            # Restrições simples de caixa/estoque
            if side == "buy" and self.cash < qty * market.price:
                return None
            if side == "sell" and self.holdings.get("ASSET", 0.0) < qty:
                return None
            return Order(agent=self, side=side, qty=qty)
        return None