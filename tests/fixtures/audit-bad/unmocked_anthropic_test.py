"""
Fixture: a test file with an unmocked `anthropic.Anthropic(...)` call.

This file exists solely so the regression gate's audit script
(`tests/audit-anthropic-mocked.py`) has a known-bad target to verify against.
The audit script must exit 1 when pointed at this file. The file is NOT
collected by pytest because its filename does not match `test_*.py`.
"""

from unittest.mock import patch  # noqa: F401  (import present but never used to wrap the call)

import anthropic


def construct_real_client():
    # Unmocked: this instantiation would hit the real API at runtime.
    return anthropic.Anthropic()


def construct_with_proper_mock():
    # This one IS mocked -- demonstrates the audit treats each call site independently.
    with patch("anthropic.Anthropic") as mock_client:
        return mock_client()
