"""Replayable log format — save/load EvalLog in JSON or msgpack."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import msgpack

from trine_eval.core.log import EvalLog


def save(
    log: EvalLog,
    path: str | Path,
    *,
    format: Literal["json", "msgpack"] = "json",
) -> None:
    """
    Persist an EvalLog to disk.

    Parameters
    ----------
    log:
        The EvalLog to save.
    path:
        Destination file path. The ``format`` parameter controls serialization;
        the file extension is NOT used to determine format here (only in ``load``).
    format:
        ``"json"`` (default) — human-readable, UTF-8.
        ``"msgpack"`` — compact binary.
    """
    path = Path(path)
    # Use model_dump(mode="json") to get a JSON-serializable dict.
    # Pydantic normalises datetimes to ISO-8601 strings, which model_validate
    # will parse back correctly on load.
    data = log.model_dump(mode="json")

    if format == "json":
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif format == "msgpack":
        path.write_bytes(msgpack.packb(data, use_bin_type=True))
    else:
        raise ValueError(f"Unsupported format: {format!r}. Must be 'json' or 'msgpack'.")


def load(path: str | Path) -> EvalLog:
    """
    Load an EvalLog from disk.

    Format is detected from the file extension:
    - ``.json`` → JSON
    - ``.msgpack`` → msgpack

    Raises
    ------
    ValueError
        If the file extension is neither ``.json`` nor ``.msgpack``.
    FileNotFoundError
        If the file does not exist.
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif suffix == ".msgpack":
        data = msgpack.unpackb(path.read_bytes(), raw=False)
    else:
        raise ValueError(
            f"Cannot detect format from extension {suffix!r}. "
            "Use '.json' or '.msgpack'."
        )

    return EvalLog.model_validate(data)
