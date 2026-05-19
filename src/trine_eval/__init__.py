"""trine-eval: A Python eval library for LLM evaluation."""

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.core.task import Task
from trine_eval.core.log import EvalLog
from trine_eval.core import registry
from trine_eval.core.decorators import task, solver, scorer, metric, tool
from trine_eval.models.anthropic import AnthropicModel

__version__ = "0.1.0"

__all__ = [
    "Sample",
    "Score",
    "Task",
    "EvalLog",
    "registry",
    "task",
    "solver",
    "scorer",
    "metric",
    "tool",
    "AnthropicModel",
    "__version__",
]
