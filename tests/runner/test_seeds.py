"""Seed reproducibility and version capture tests."""
from __future__ import annotations

import os
import random

from trine_eval.runner.seeds import seed_all
from trine_eval.runner.versions import capture_versions


def test_seed_all_random_reproducible() -> None:
    """Same seed produces same random sequence."""
    seed_all(42)
    seq1 = [random.random() for _ in range(5)]

    seed_all(42)
    seq2 = [random.random() for _ in range(5)]

    assert seq1 == seq2


def test_seed_all_sets_pythonhashseed() -> None:
    """seed_all sets PYTHONHASHSEED environment variable."""
    seed_all(123)
    assert os.environ.get("PYTHONHASHSEED") == "123"


def test_different_seeds_produce_different_sequences() -> None:
    """Different seeds produce different random sequences."""
    seed_all(1)
    seq1 = [random.random() for _ in range(5)]

    seed_all(2)
    seq2 = [random.random() for _ in range(5)]

    assert seq1 != seq2


def test_capture_versions_returns_required_keys() -> None:
    """capture_versions returns all required version keys."""
    info = capture_versions("claude-opus-4-7")
    assert "trine_eval" in info
    assert "model_id" in info
    assert "platform" in info
    assert "python_version" in info
    assert info["model_id"] == "claude-opus-4-7"
    assert info["trine_eval"] == "0.1.0"
