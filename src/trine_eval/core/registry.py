from __future__ import annotations

from typing import Callable

# Module-level registries for each decorator type.
# Functions are registered by their __name__ when decorated.
tasks: dict[str, Callable] = {}
solvers: dict[str, Callable] = {}
scorers: dict[str, Callable] = {}
metrics: dict[str, Callable] = {}
tools: dict[str, Callable] = {}
