from __future__ import annotations

from typing import Callable, TypeVar

from trine_eval.core import registry as _registry

F = TypeVar("F", bound=Callable)


def task(fn: F) -> F:
    """Register a function as a task in the tasks registry."""
    _registry.tasks[fn.__name__] = fn
    return fn


def solver(fn: F) -> F:
    """Register a function as a solver in the solvers registry."""
    _registry.solvers[fn.__name__] = fn
    return fn


def scorer(fn: F) -> F:
    """Register a function as a scorer in the scorers registry."""
    _registry.scorers[fn.__name__] = fn
    return fn


def metric(fn: F) -> F:
    """Register a function as a metric in the metrics registry."""
    _registry.metrics[fn.__name__] = fn
    return fn


def tool(fn: F) -> F:
    """Register a function as a tool in the tools registry."""
    _registry.tools[fn.__name__] = fn
    return fn
