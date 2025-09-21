from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import pandas as pd
import random

from .market import Market
from .investidor import BaseAgent

@dataclass
class Simulation:
    seed: Optional[int] = None
    market: Market = field(default_factory=lambda: Market(price0=100.0))
    agents: List[BaseAgent] = field(default_factory=list)
    log: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self.rng = random.Random(self.seed)

    def add_agent(self, agent: BaseAgent) -> None:
        self.agents.append(agent)

    def run(self, steps: int = 100) -> None:
        for t in range(steps):
            self.market.step(self.agents)
            snapshot = {"t": t, "price": self.market.price}
            for ag in self.agents:
                snapshot[f"cash:{ag.name}"] = ag.cash
                snapshot[f"asst:{ag.name}"] = ag.holdings.get("ASSET", 0.0)
            self.log.append(snapshot)

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.log)