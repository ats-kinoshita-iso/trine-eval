"""Tests for the decorator registry: @task, @solver, @scorer, @metric, @tool."""

from __future__ import annotations

from trine_eval.core import registry
from trine_eval.core.decorators import task, solver, scorer, metric, tool


SENTINEL_TASK = object()
SENTINEL_SOLVER = object()
SENTINEL_SCORER = object()
SENTINEL_METRIC = object()
SENTINEL_TOOL = object()


class TestTaskDecorator:
    def test_registers_by_name(self) -> None:
        @task
        def my_task_func():
            return SENTINEL_TASK

        assert "my_task_func" in registry.tasks

    def test_returns_sentinel_value(self) -> None:
        @task
        def task_returns_sentinel():
            return SENTINEL_TASK

        fn = registry.tasks["task_returns_sentinel"]
        assert fn() is SENTINEL_TASK

    def test_original_function_unchanged(self) -> None:
        @task
        def task_identity():
            return 42

        assert task_identity() == 42


class TestSolverDecorator:
    def test_registers_by_name(self) -> None:
        @solver
        def my_solver_func():
            return SENTINEL_SOLVER

        assert "my_solver_func" in registry.solvers

    def test_callable_executes(self) -> None:
        @solver
        def solver_executes():
            return SENTINEL_SOLVER

        fn = registry.solvers["solver_executes"]
        assert fn() is SENTINEL_SOLVER

    def test_original_function_unchanged(self) -> None:
        @solver
        def solver_identity():
            return 99

        assert solver_identity() == 99


class TestScorerDecorator:
    def test_registers_by_name(self) -> None:
        @scorer
        def my_scorer_func():
            return SENTINEL_SCORER

        assert "my_scorer_func" in registry.scorers

    def test_returns_sentinel_value(self) -> None:
        @scorer
        def scorer_returns_sentinel():
            return SENTINEL_SCORER

        fn = registry.scorers["scorer_returns_sentinel"]
        assert fn() is SENTINEL_SCORER

    def test_original_function_unchanged(self) -> None:
        @scorer
        def scorer_identity():
            return "score"

        assert scorer_identity() == "score"


class TestMetricDecorator:
    def test_registers_by_name(self) -> None:
        @metric
        def my_metric_func():
            return SENTINEL_METRIC

        assert "my_metric_func" in registry.metrics

    def test_returns_sentinel_value(self) -> None:
        @metric
        def metric_returns_sentinel():
            return SENTINEL_METRIC

        fn = registry.metrics["metric_returns_sentinel"]
        assert fn() is SENTINEL_METRIC

    def test_original_function_unchanged(self) -> None:
        @metric
        def metric_identity():
            return 3.14

        assert metric_identity() == 3.14


class TestToolDecorator:
    def test_registers_by_name(self) -> None:
        @tool
        def my_tool_func():
            return SENTINEL_TOOL

        assert "my_tool_func" in registry.tools

    def test_callable_executes(self) -> None:
        @tool
        def tool_executes():
            return SENTINEL_TOOL

        fn = registry.tools["tool_executes"]
        assert fn() is SENTINEL_TOOL

    def test_original_function_unchanged(self) -> None:
        @tool
        def tool_identity():
            return "tool result"

        assert tool_identity() == "tool result"
