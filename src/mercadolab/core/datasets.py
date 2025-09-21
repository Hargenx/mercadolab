from __future__ import annotations
import numpy as np
import pandas as pd

def synthetic_returns(n: int = 252, mu: float = 0.0, sigma: float = 0.01, seed: int = 42) -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sigma, size=n)
    return pd.Series(r, name="r")