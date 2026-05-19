"""Version and environment capture for EvalLog provenance."""
from __future__ import annotations

import platform
import sys


def capture_versions(model_id: str) -> dict[str, str]:
    """
    Capture library and environment versions for reproducibility metadata.

    Returns a dict suitable for insertion into ``EvalLog.metadata["versions"]``.

    Parameters
    ----------
    model_id:
        The model identifier string (e.g., ``"claude-opus-4-7"``).

    Returns
    -------
    dict[str, str]
        Keys: ``trine_eval``, ``model_id``, ``platform``, ``python_version``.
    """
    import trine_eval

    return {
        "trine_eval": trine_eval.__version__,
        "model_id": model_id,
        "platform": platform.system(),
        "python_version": sys.version,
    }
