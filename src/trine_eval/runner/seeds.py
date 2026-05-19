"""Deterministic seed utilities for reproducible eval runs."""
from __future__ import annotations

import os
import random


def seed_all(seed: int) -> None:
    """
    Seed all relevant random sources for reproducible eval runs.

    Covers: ``random.seed``, ``os.environ["PYTHONHASHSEED"]``,
    and ``numpy.random.seed`` when numpy is installed.

    Parameters
    ----------
    seed:
        Integer seed value. Use a fixed constant (e.g., ``42``) for
        reproducible runs, or a timestamp for varied-but-logged runs.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    try:
        import numpy as np  # type: ignore[import-not-found]
        np.random.seed(seed)
    except ImportError:
        pass  # numpy is optional
