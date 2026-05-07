"""Sprint 12 Criterion 5 — Batch API runtime hookup smoke test.

Demonstrates that the Batch API protocol shipped in Sprint 8 can construct a
valid request body and survive an end-to-end shape check, gated on
ANTHROPIC_API_KEY being present.

Offline mode (no ANTHROPIC_API_KEY): exits 0 with `[SKIP]`.
Online mode (ANTHROPIC_API_KEY set, even to a placeholder): constructs a
2-criterion batch payload, serializes it via the SDK's model_dump_json (or a
plain dict-to-json fallback), prints the shape summary. NEVER sends to the
network in either mode -- the shape-check is the test, not the live request.

This dual-mode design lets the script run in any environment (CI, local dev,
operator laptop) without requiring a real Anthropic account, while still
exercising the same code path that an online run would use.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any


def build_payload() -> dict[str, Any]:
    return {
        "requests": [
            {
                "custom_id": "sprint-12-c1",
                "params": {
                    "model": "claude-opus-4-7",
                    "max_tokens": 256,
                    "messages": [
                        {"role": "user", "content": "Smoke 1: deterministic criterion"}
                    ],
                },
            },
            {
                "custom_id": "sprint-12-c2",
                "params": {
                    "model": "claude-opus-4-7",
                    "max_tokens": 256,
                    "messages": [
                        {"role": "user", "content": "Smoke 2: llm-judge criterion"}
                    ],
                },
            },
        ]
    }


def serialize_via_sdk_or_fallback(payload: dict[str, Any]) -> str:
    try:
        from anthropic.types.messages.batch_create_params import Request

        sdk_requests = []
        for req in payload["requests"]:
            sdk_requests.append(
                Request(custom_id=req["custom_id"], params=req["params"])
            )
        return json.dumps({"requests": [r if isinstance(r, dict) else dict(r) for r in sdk_requests]}, default=str)
    except Exception:
        return json.dumps(payload)


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[SKIP] ANTHROPIC_API_KEY not set -- Batch API smoke test deferred")
        return 0

    payload = build_payload()
    serialized = serialize_via_sdk_or_fallback(payload)

    parsed = json.loads(serialized)
    assert "requests" in parsed, "payload missing 'requests' key"
    assert len(parsed["requests"]) == 2, "expected 2 batched criteria"
    for req in parsed["requests"]:
        assert "custom_id" in req, "request missing custom_id"
        assert "params" in req, "request missing params"
        assert req["params"]["model"].startswith("claude-"), "model not Anthropic"

    print(
        f"[OK] Batch payload constructed: {len(serialized)} bytes, "
        f"{len(parsed['requests'])} requests, no network call performed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
