# Rubric Decision Guide

This directory contains the evaluation rubrics used by trine-eval. Choose the rubric that
matches your project type. Two rubrics — `eval-harness` and `harness-build` — both apply to
harness-adjacent projects; see the disambiguation section below.

## Available Rubrics

| Rubric | File | When to Pick |
|--------|------|--------------|
| `web-app` | [web-app.md](web-app.md) | Web applications: React, Vue, Next.js, and similar. Use when to pick this: browser-based UIs with routing, forms, and user interaction. |
| `rag-system` | [rag-system.md](rag-system.md) | Retrieval-augmented generation systems. Use when to pick this: vector stores, embedding pipelines, retrieval quality, and faithfulness grading. |
| `cli-tool` | [cli-tool.md](cli-tool.md) | Command-line tools. Use when to pick this: projects that expose a CLI with argument parsing, error messages, and Unix exit codes. |
| `api-service` | [api-service.md](api-service.md) | REST or GraphQL APIs. Use when to pick this: HTTP services requiring status code validation, authentication, and concurrency testing. |
| `eval-harness` | [eval-harness.md](eval-harness.md) | **Meta layer** — Eval-driven development harnesses: methodology completeness, grading architecture, contract quality, context engineering. Use when to pick this: when you are building or auditing a Planner-Generator-Evaluator harness and the primary artifact under evaluation is the eval infrastructure itself. |
| `harness-build` | [harness-build.md](harness-build.md) | **Runtime layer** — Agent runtime harnesses: agentic loops, tool registries, sandboxing, governance. Use when to pick this: when you are building the engineering infrastructure that surrounds and controls an LLM agent and conformance to playbook stages is the primary concern. |

## Meta vs. Runtime

The two harness-adjacent rubrics occupy different layers of the stack:

- **`eval-harness` is the meta layer.** It grades the eval methodology itself — whether your Planner-Generator-Evaluator harness implements the correct contract format, grader hierarchy, retry logic, and sprint workflow. It applies when the deliverable is the eval infrastructure.

- **`harness-build` is the runtime layer.** It grades an agent runtime harness for conformance to the playbook's stages — whether the agentic loop is bounded, tools are sandboxed, and governance is correctly placed. It applies when the deliverable is the control plane that governs a live agent.

## Disambiguating eval-harness vs harness-build

These two rubrics cover adjacent domains. The key question is: **what is the primary artifact under evaluation?**

- **Use `eval-harness`** when the primary artifact is the *eval infrastructure itself* — the contract template, the grader hierarchy, the retry logic, the sprint workflow. The meta layer rubric grades whether the harness does eval-driven development correctly.

- **Use `harness-build`** when the primary artifact is the *agent runtime* — the agentic loop, the tool registry, the sandbox declaration, the governance escalation path. The runtime layer rubric grades whether the agent's control infrastructure conforms to the playbook's stages and hard-threshold gates.

**Overlap zone:** If you are building an eval harness that *also* runs agents internally (e.g., a harness whose Generator and Evaluator are themselves agentic loops), choose the rubric that governs the primary deliverable:
- If the sprint is adding or auditing eval methodology (weighted criteria, grader types, contract format) → use `eval-harness`.
- If the sprint is building or hardening the agent runtime layer (loop bounds, sandboxing, governance) → use `harness-build`.

When in doubt, `rubric` can be overridden per-sprint in `.harness/config.json`.
