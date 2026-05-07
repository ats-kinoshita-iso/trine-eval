# Transcripts

Structured JSON records of evaluator runs. One file per evaluation, written by the harness-sprint workflow after each Evaluator subagent finishes.

## File naming

- Multi-trial mode (`config.trials > 1`): `sprint-{NN}-r{R}-t{T}.json` — one file per trial within a round.
- Single-trial mode (`config.trials == 1`, the default): `sprint-{NN}-r{R}.json` — one file per round.

Naming mirrors the markdown eval files in `.harness/evals/`. Each transcript file pairs 1:1 with the eval markdown file produced by the same evaluator run.

## What is a transcript?

A transcript is the structured-data sibling of the markdown eval. The Evaluator emits a JSON trailer at the end of its eval markdown file under a `## Transcript Trailer` section (see `agents/evaluator.md`). After the eval lands, the harness-sprint workflow extracts that trailer block, parses it as JSON, and writes it here. The markdown remains the human-readable eval; this directory is the machine-readable audit channel.

## Why structured transcripts?

- **Calibration auditing.** A FAIL verdict says *what* failed; the transcript shows *how* the evaluator reached it — what tools were called, what evidence was weighed, and where the conclusion came from. The harness-summary skill links the transcript next to FAIL criteria and grader-disagreement entries so a human reviewer can audit the verdict.
- **Cross-run analysis.** Repeated patterns (failed tool calls, ambiguous criteria, runaway thinking time) only show up when transcripts can be parsed and aggregated.
- **Forward-compatible audit trail.** Sprint 10 will add `verified_via_command` adversarial-hygiene flags inside this same JSON channel without renegotiating the schema.

## Schema and configuration

The full schema (top-level fields, JSON shape, capture/retention knobs) is documented in `rules/harness-conventions.md` under the **Transcript Schema** section. The two config knobs that gate this directory are:

- `config.transcripts.capture` (default `true`) — when truthy, the harness extracts and writes transcripts here. When `false`, capture is skipped.
- `config.transcripts.retain_days` (default `30`) — declared retention window. Cleanup is policy-only in Sprint 9; actual deletion runs out-of-band or in a future sprint.

## Empty until Sprint 9 / Sprint 10 evals run

This README is committed before any transcripts exist. Files appear as the harness runs new sprints whose evaluator agent emits a trailer. Pre-Sprint-9 evaluator runs do not produce trailers, so this directory remains empty for legacy sprints — the protocol applies going forward.
