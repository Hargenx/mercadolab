from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import math
import random

from .investidor import Order, BaseAgent

@dataclass
class Market:
    price: float = 100.0
    step_vol: float = 0.01  # volatilidade do passo (desvio-padrão de retornos)
    rng: random.Random = field(default_factory=random.Random)

    def __init__(self, price0: float = 100.0, step_vol: float = 0.01, seed: Optional[int] = None):
        self.price = price0
        self.step_vol = step_vol
        self.rng = random.Random(seed)

    def evolve_price(self) -> None:
        # Caminho aleatório geométrico discreto simples
        r = self.rng.normalvariate(0.0, self.step_vol)
        self.price *= math.exp(r)

    def execute(self, orders: List[Order]) -> None:
        # Motor de execução simplificado: todas ordens são "market" ao preço atual
        for od in orders:
            od.agent.on_fill(od.side, od.qty, self.price)
        # Pequeno impacto de preço proporcional ao desequilíbrio
        imbalance = sum((+o.qty if o.side == "buy" else -o.qty) for o in orders)
        self.price *= (1.0 + 0.0005 * imbalance)

    def step(self, agents: List[BaseAgent]) -> None:
        # 1) preço de fundo (microestrutura/ruído)
        self.evolve_price()
        # 2) agentes decidem e executamos
        orders = []
        for ag in agents:
            od = ag.decide(self)
            if od is not None:
                orders.append(od)
        if orders:
            self.execute(orders)