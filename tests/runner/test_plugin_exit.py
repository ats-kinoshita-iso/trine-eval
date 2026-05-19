"""
Test for pytest plugin exit-100 behaviour.

This test file deliberately causes a trine-eval score below threshold (0.0 < 1.0),
which should trigger the plugin's exit-100 override in pytest_sessionfinish.

The C4 verification command runs this file as a sub-pytest and checks that the
exit code is 100:

    bash -c 'uv run pytest tests/runner/test_plugin_exit.py --tb=short 2>&1; \\
             CODE=$?; [ "$CODE" = "100" ] && echo PLUGIN_OK || ...'
"""
from __future__ import annotations

import pytest


@pytest.mark.trine_eval
def test_failing_trine_eval_score(record_trine_eval_score: object) -> None:
    """
    This test records a score of 0.0, which is below the default threshold of 1.0.
    The plugin should override the exit code to 100 when this runs.
    """
    # Cast to the actual fixture type to call it
    record_fn = record_trine_eval_score  # type: ignore[assignment]
    record_fn(0.0)  # score=0.0 < threshold=1.0 → sets session._trine_eval_failed=True
