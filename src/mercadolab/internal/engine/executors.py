from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Executor
from typing import Literal


def make_executor(
    kind: Literal["thread", "process"] = "thread", max_workers: int | None = None
) -> Executor:
    if kind == "process":
        return ProcessPoolExecutor(max_workers=max_workers)
    return ThreadPoolExecutor(max_workers=max_workers)
