"""
trine-eval pytest plugin.

Hooks into pytest to exit with code 100 when any trine-eval-scored test
scores below the configured threshold (--trine-eval-threshold, default 1.0).

Usage
-----
Mark a test with ``@pytest.mark.trine_eval`` and call
``record_trine_eval_score(request, score)`` to register a score.
If any score is below the threshold, pytest exits 100 instead of the
standard exit code.
"""
from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add --trine-eval-threshold CLI option."""
    parser.addoption(
        "--trine-eval-threshold",
        type=float,
        default=1.0,
        help="Minimum score threshold for trine-eval tests (default: 1.0). "
             "Any test scoring below this exits pytest with code 100.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register the trine_eval marker."""
    config.addinivalue_line(
        "markers",
        "trine_eval: mark test as a trine-eval scored test",
    )


@pytest.fixture
def trine_eval_threshold(request: pytest.FixtureRequest) -> float:
    """Fixture that returns the configured threshold."""
    return float(request.config.getoption("--trine-eval-threshold", default=1.0))


@pytest.fixture
def record_trine_eval_score(request: pytest.FixtureRequest) -> "RecordScore":
    """Fixture for recording a trine-eval score in a test."""
    return RecordScore(request)


class RecordScore:
    """Helper for recording trine-eval scores within a test."""

    def __init__(self, request: pytest.FixtureRequest) -> None:
        self._request = request

    def __call__(self, score: float) -> None:
        """Record a score. Values below threshold will trigger exit 100."""
        threshold = float(
            self._request.config.getoption("--trine-eval-threshold", default=1.0)
        )
        if score < threshold:
            session = self._request.session
            session._trine_eval_failed = True  # type: ignore[attr-defined]


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Override exit code to 100 when any trine-eval score failed threshold."""
    if getattr(session, "_trine_eval_failed", False):
        session.exitstatus = 100
