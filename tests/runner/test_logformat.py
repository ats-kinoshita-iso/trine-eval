"""Log format round-trip tests — JSON and msgpack."""
from __future__ import annotations

from datetime import datetime, timezone

from trine_eval.core.log import EvalLog
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.runner.logformat import load, save


def _make_log() -> EvalLog:
    """Build a non-trivial EvalLog with 2+ samples, 2+ scores, non-empty aggregate."""
    return EvalLog(
        task_name="test-task",
        samples=[
            Sample(id="1", input="hello", target="world"),
            Sample(id="2", input="foo", target="bar"),
        ],
        scores=[
            Score(value=1.0, answer="world", explanation="exact match"),
            Score(value=0.0, answer="baz", explanation="wrong"),
        ],
        model="claude-opus-4-7",
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        aggregate={"accuracy": 0.5},
        metadata={"cap_hit": "token_limit"},
    )


def test_json_round_trip(tmp_path: object) -> None:
    """save → load in JSON format produces an equal EvalLog."""
    import pathlib
    path = pathlib.Path(str(tmp_path)) / "log.json"
    log = _make_log()

    save(log, path, format="json")
    loaded = load(path)

    assert loaded == log


def test_msgpack_round_trip(tmp_path: object) -> None:
    """save → load in msgpack format produces an equal EvalLog."""
    import pathlib
    path = pathlib.Path(str(tmp_path)) / "log.msgpack"
    log = _make_log()

    save(log, path, format="msgpack")
    loaded = load(path)

    assert loaded == log


def test_json_file_is_human_readable(tmp_path: object) -> None:
    """JSON output is valid UTF-8 text containing the task name."""
    import json
    import pathlib
    path = pathlib.Path(str(tmp_path)) / "log.json"
    log = _make_log()
    save(log, path, format="json")
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    assert data["task_name"] == "test-task"
    assert data["aggregate"]["accuracy"] == 0.5
