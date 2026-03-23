from __future__ import annotations

from concurrent.futures import Executor, ThreadPoolExecutor


def make_executor(max_workers: int | None = None) -> Executor:
    """Cria o executor padrão utilizado pelo scheduler."""
    return ThreadPoolExecutor(max_workers=max_workers)
