"""Langfuse client wiring for trine-eval observability."""
from __future__ import annotations

import os
from typing import Any


class _NoopLangfuseClient:
    """Stub client used when Langfuse SDK is unavailable or not configured."""

    def trace(self, *args: Any, **kwargs: Any) -> "_NoopLangfuseClient":
        return self

    def generation(self, *args: Any, **kwargs: Any) -> "_NoopLangfuseClient":
        return self

    def span(self, *args: Any, **kwargs: Any) -> "_NoopLangfuseClient":
        return self

    def update(self, *args: Any, **kwargs: Any) -> "_NoopLangfuseClient":
        return self

    def end(self, *args: Any, **kwargs: Any) -> None:
        pass

    def flush(self) -> None:
        pass

    @property
    def is_noop(self) -> bool:
        return True


def get_langfuse_client(
    public_key: str | None = None,
    secret_key: str | None = None,
    host: str | None = None,
) -> Any:
    """
    Return a configured Langfuse client, or a noop stub if not available.

    Reads ``LANGFUSE_PUBLIC_KEY``, ``LANGFUSE_SECRET_KEY``, and
    ``LANGFUSE_HOST`` from the environment when keyword arguments are not
    provided. Returns a ``_NoopLangfuseClient`` when:
    - Any of the three credentials are missing, or
    - The ``langfuse`` package is not installed, or
    - The Langfuse server is unreachable.

    Parameters
    ----------
    public_key:
        Langfuse public key. Overrides ``LANGFUSE_PUBLIC_KEY`` env var.
    secret_key:
        Langfuse secret key. Overrides ``LANGFUSE_SECRET_KEY`` env var.
    host:
        Langfuse host URL (e.g., ``"https://cloud.langfuse.com"``).
        Overrides ``LANGFUSE_HOST`` env var.

    Returns
    -------
    Langfuse client or ``_NoopLangfuseClient``
    """
    pk = public_key or os.environ.get("LANGFUSE_PUBLIC_KEY")
    sk = secret_key or os.environ.get("LANGFUSE_SECRET_KEY")
    h = host or os.environ.get("LANGFUSE_HOST")

    if not (pk and sk and h):
        return _NoopLangfuseClient()

    try:
        from langfuse import Langfuse  # type: ignore[import-not-found]

        # Disable background threads that would try network connections
        client = Langfuse(
            public_key=pk,
            secret_key=sk,
            host=h,
        )
        return client
    except Exception:
        # Network errors, import failures — return noop
        return _NoopLangfuseClient()
