"""OpenTelemetry tracer setup for trine-eval."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Literal

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Module-level tracer provider (replaced by init_tracer)
_provider: TracerProvider | None = None
_in_memory_exporter: InMemorySpanExporter | None = None


def init_tracer(
    exporter: Literal["noop", "langfuse", "in_memory"] = "noop",
    service_name: str = "trine-eval",
) -> TracerProvider:
    """
    Initialize and register a TracerProvider.

    Parameters
    ----------
    exporter:
        ``"noop"`` — No spans are exported (safe default for tests/CI).
        ``"langfuse"`` — Export to Langfuse via OTLP-HTTP when env vars are set;
                         falls back to noop if env vars are missing.
        ``"in_memory"`` — Store spans in memory for test inspection; retrieve with
                          ``get_in_memory_exporter()``.
    service_name:
        OTel service.name resource attribute.

    Returns
    -------
    TracerProvider
        The configured provider (also set as the global OTel provider).
    """
    global _provider, _in_memory_exporter

    from opentelemetry.sdk.resources import Resource

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if exporter == "noop":
        # No processor — spans are silently discarded
        pass

    elif exporter == "in_memory":
        mem_exporter = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(mem_exporter))
        _in_memory_exporter = mem_exporter

    elif exporter == "langfuse":
        langfuse_host = os.environ.get("LANGFUSE_HOST")
        if langfuse_host:
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                    OTLPSpanExporter,
                )
                otlp_exporter = OTLPSpanExporter(
                    endpoint=f"{langfuse_host.rstrip('/')}/api/public/otel/v1/traces",
                )
                provider.add_span_processor(SimpleSpanProcessor(otlp_exporter))
            except Exception:
                # Fall back to noop if OTLP exporter setup fails
                pass
        # else: no LANGFUSE_HOST → noop silently

    else:
        raise ValueError(f"Unknown exporter: {exporter!r}. Must be 'noop', 'langfuse', or 'in_memory'.")

    # Reset the global provider so we can override it (needed for test isolation)
    try:
        from opentelemetry.sdk.trace import TracerProvider as _TP
        trace._TRACER_PROVIDER_SET_ONCE._done = False  # type: ignore[attr-defined]
    except Exception:
        pass

    trace.set_tracer_provider(provider)
    _provider = provider
    return provider


def get_tracer(name: str = "trine-eval") -> trace.Tracer:
    """Return a tracer from the current global provider."""
    return trace.get_tracer(name)


def get_in_memory_exporter() -> InMemorySpanExporter | None:
    """Return the in-memory exporter if init_tracer was called with exporter='in_memory'."""
    return _in_memory_exporter


@contextmanager
def trace_step(name: str) -> Generator[trace.Span, None, None]:
    """
    Context manager that wraps a block in a named OTel span.

    Usage::

        with trace_step("solve-sample") as span:
            span.set_attribute("sample.id", sample.id)
            result = solver(sample)
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        yield span
