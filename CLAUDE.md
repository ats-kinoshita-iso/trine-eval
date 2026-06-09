# trine-eval

This repo is a Claude Code plugin marketplace containing the trine-eval plugin — a three-agent
eval-driven development harness — alongside the `trine_eval` Python eval library that the harness
is designed to build and exercise.

## Repository layout

- **`plugins/trine-eval/`** — the Claude Code plugin (Planner-Generator-Evaluator agents, skills,
  rubrics). This is the methodology / build-vehicle layer.
- **`src/trine_eval/`** — the Python eval library (runner, scorers, metrics, Anthropic model
  wrapper, OpenTelemetry/Langfuse observability, pytest plugin). This is the runtime layer.
- **`.harness/`** — the on-disk build journal the agents communicate through.
- **`.council/`** — **git-ignored**. Governance is provided by the separate henkaten-council
  plugin; any `.council/` state is an artifact of running that plugin against this repo, not a
  part of trine-eval itself. trine-eval exposes only an opt-in, config-gated governance seam
  (off by default) — it does not depend on any governance layer.

See [`REPOSITORY-MAP.md`](REPOSITORY-MAP.md) for a full path-by-path classification of product
vs. development infrastructure vs. dogfooding byproducts, with a removal/breakage analysis.

## Skills

- `/harness-kickoff` — Initialize harness with a product prompt
- `/harness-sprint` — Run one sprint through contract→build→eval cycle
- `/harness-summary` — Generate cross-sprint evaluation report

The plugin's rubric inventory includes both `eval-harness` (meta layer — grades eval methodology
such as contract format, grader hierarchy, and sprint workflow) and `harness-build` (runtime
layer — grades agent runtime harnesses for conformance to playbook stages). See
`plugins/trine-eval/skills/eval-rubric/rubrics/README.md` for the full decision guide on which
rubric to use.

## Python library

- Use `uv` for everything: `uv run pytest`, `uv run trine-eval run <task>`, `uv run ruff`,
  `uv run mypy`.
- Strict `mypy` + `ruff`; type annotations required on all signatures.

## Conventions

- Agent communication happens via files in `.harness/` only
- JSON for structured data, markdown for prose
- Sprint contracts are the source of truth for "done"
- Eval results are append-only — never modify prior sprints
