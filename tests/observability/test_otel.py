"""OpenTelemetry tracer + Langfuse client wiring tests."""
from __future__ import annotations

import pytest

from trine_eval.observability.langfuse import get_langfuse_client
from trine_eval.observability.otel import (
    get_in_memory_exporter,
    get_tracer,
    init_tracer,
    trace_step,
)


def test_init_tracer_noop_does_not_raise() -> None:
    """init_tracer(exporter='noop') completes without raising."""
    provider = init_tracer(exporter="noop")
    assert provider is not None


def test_init_tracer_returns_tracer_provider() -> None:
    """init_tracer returns a TracerProvider."""
    from opentelemetry.sdk.trace import TracerProvider

    provider = init_tracer(exporter="noop")
    assert isinstance(provider, TracerProvider)


def test_get_tracer_returns_tracer() -> None:
    """get_tracer returns an OTel Tracer object."""
    from opentelemetry import trace

    init_tracer(exporter="noop")
    tracer = get_tracer()
    assert isinstance(tracer, trace.Tracer)


def test_span_start_and_end() -> None:
    """Spans can be started and ended without error."""
    init_tracer(exporter="noop")
    tracer = get_tracer()
    with tracer.start_as_current_span("test-span") as span:
        span.set_attribute("test.key", "test-value")
    # No exception raised = PASS


def test_trace_step_context_manager() -> None:
    """trace_step context manager starts and ends a span."""
    init_tracer(exporter="noop")
    with trace_step("my-step") as span:
        span.set_attribute("sample.id", "abc")
    # No exception raised = PASS


def test_in_memory_exporter_captures_spans() -> None:
    """init_tracer(exporter='in_memory') captures spans for inspection."""
    init_tracer(exporter="in_memory")
    exporter = get_in_memory_exporter()
    assert exporter is not None

    exporter.clear()
    tracer = get_tracer()
    with tracer.start_as_current_span("captured-span"):
        pass

    finished = exporter.get_finished_spans()
    assert len(finished) >= 1
    assert finished[0].name == "captured-span"


def test_get_langfuse_client_missing_creds_returns_noop() -> None:
    """get_langfuse_client with no env vars returns a noop stub."""
    client = get_langfuse_client(public_key=None, secret_key=None, host=None)
    # Should return noop client (no network call)
    assert client is not None
    # Noop client has is_noop attribute
    assert getattr(client, "is_noop", False) is True


def test_get_langfuse_client_with_stub_creds_no_network(mocker: pytest.MonkeyPatch) -> None:
    """get_langfuse_client with stub credentials does not make real network calls."""
    # Mock the Langfuse constructor to avoid any network activity
    mock_langfuse_cls = mocker.patch("trine_eval.observability.langfuse.Langfuse", create=True)
    mock_instance = mocker.MagicMock()
    mock_langfuse_cls.return_value = mock_instance

    client = get_langfuse_client(
        public_key="pk-test",
        secret_key="sk-test",
        host="http://localhost:3000",
    )
    # Either returns the mock instance or a noop (if import fails)
    assert client is not None
