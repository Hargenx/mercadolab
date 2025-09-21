from __future__ import annotations
from importlib.metadata import entry_points
from typing import Dict, Type
from ..core.investidor import BaseAgent

def load_plugins() -> Dict[str, Type[BaseAgent]]:
    # Carrega entry-points do grupo "mercadolab.plugins"
    result: Dict[str, Type[BaseAgent]] = {}
    eps = entry_points(group="mercadolab.plugins")
    for ep in eps:
        try:
            cls = ep.load()
            if isinstance(cls, type) and issubclass(cls, BaseAgent):
                result[ep.name] = cls
        except Exception as e:
            import warnings
            warnings.warn(f"Erro ao carregar plugin '{ep.name}': {e}")
            # Ignora plugins inválidos para não quebrar a CLI
            continue
    return result