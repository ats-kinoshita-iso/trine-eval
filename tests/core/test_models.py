"""Tests for core Pydantic models: Sample, Score, Task, EvalLog."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
import pydantic

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.core.task import Task
from trine_eval.core.log import EvalLog


class TestSample:
    def test_basic_construction(self) -> None:
        s = Sample(id="x", input="hello", target="world")
        assert s.id == "x"
        assert s.input == "hello"
        assert s.target == "world"

    def test_model_dump_id(self) -> None:
        s = Sample(id="x", input="hello", target="world")
        assert s.model_dump()["id"] == "x"

    def test_target_is_optional(self) -> None:
        s = Sample(id="y", input="hi")
        assert s.target is None

    def test_metadata_default_empty(self) -> None:
        s = Sample(id="z", input="test")
        assert s.metadata == {}

    def test_metadata_stored(self) -> None:
        s = Sample(id="m", input="test", metadata={"key": "value"})
        assert s.metadata["key"] == "value"

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            Sample(input="hello")  # type: ignore[call-arg]

    def test_json_round_trip(self) -> None:
        s = Sample(id="rt", input="round-trip", target="expected", metadata={"n": 1})
        json_str = s.model_dump_json()
        s2 = Sample.model_validate_json(json_str)
        assert s2.id == s.id
        assert s2.input == s.input
        assert s2.target == s.target
        assert s2.metadata == s.metadata


class TestScore:
    def test_basic_construction(self) -> None:
        sc = Score(value=0.9, answer="42", explanation="correct")
        assert sc.value == 0.9
        assert sc.answer == "42"
        assert sc.explanation == "correct"

    def test_value_only(self) -> None:
        sc = Score(value=1.0)
        assert sc.value == 1.0
        assert sc.answer is None
        assert sc.explanation is None

    def test_missing_value_raises(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            Score()  # type: ignore[call-arg]

    def test_invalid_value_type_raises(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            Score(value="not-a-float")  # type: ignore[arg-type]

    def test_json_round_trip(self) -> None:
        sc = Score(value=0.75, answer="ans", explanation="exp", metadata={"k": "v"})
        sc2 = Score.model_validate_json(sc.model_dump_json())
        assert sc2.value == sc.value
        assert sc2.answer == sc.answer
        assert sc2.explanation == sc.explanation


class TestTask:
    def test_basic_construction(self) -> None:
        samples = [Sample(id="1", input="a")]
        t = Task(name="my-task", dataset=samples)
        assert t.name == "my-task"
        assert len(t.dataset) == 1

    def test_optional_fields_default_none(self) -> None:
        t = Task(name="t", dataset=[])
        assert t.solver is None
        assert t.scorer is None
        assert t.metric is None

    def test_with_registered_names(self) -> None:
        t = Task(name="t", dataset=[], solver="my_solver", scorer="my_scorer")
        assert t.solver == "my_solver"
        assert t.scorer == "my_scorer"

    def test_missing_name_raises(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            Task(dataset=[])  # type: ignore[call-arg]

    def test_json_round_trip(self) -> None:
        t = Task(name="t", dataset=[Sample(id="1", input="x")])
        t2 = Task.model_validate_json(t.model_dump_json())
        assert t2.name == t.name
        assert len(t2.dataset) == 1
        assert t2.dataset[0].id == "1"


class TestEvalLog:
    def _make_log(self) -> EvalLog:
        return EvalLog(
            task_name="demo",
            samples=[Sample(id="1", input="hello")],
            scores=[Score(value=0.9)],
            model="claude-opus-4-7",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    def test_basic_construction(self) -> None:
        log = self._make_log()
        assert log.task_name == "demo"
        assert log.model == "claude-opus-4-7"

    def test_aggregate_default_empty(self) -> None:
        log = self._make_log()
        assert log.aggregate == {}

    def test_aggregate_stored(self) -> None:
        log = EvalLog(
            task_name="t",
            samples=[],
            scores=[],
            model="m",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            aggregate={"accuracy": 0.9},
        )
        assert log.aggregate["accuracy"] == 0.9

    def test_missing_required_raises(self) -> None:
        with pytest.raises(pydantic.ValidationError):
            EvalLog(task_name="t", samples=[], scores=[], model="m")  # type: ignore[call-arg]

    def test_json_round_trip(self) -> None:
        log = self._make_log()
        log2 = EvalLog.model_validate_json(log.model_dump_json())
        assert log2.task_name == log.task_name
        assert log2.model == log.model
        assert log2.timestamp == log.timestamp
