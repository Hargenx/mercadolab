"""
MercadoLab — Laboratório de simulações baseadas em agentes para mercados.

API estável: 0.1.x
"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("mercadolab")
except PackageNotFoundError:  # pragma: no cover - during local dev without install
    __version__ = "0.1.0"