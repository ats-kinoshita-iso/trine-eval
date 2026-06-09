# Repository map: product vs. development byproducts

This repo mixes three different kinds of content: the **shipped trine-eval product**, the
**development infrastructure** that builds and verifies it, and **dogfooding byproducts** left
behind by using trine-eval to build itself. This document classifies every path so contributors
can tell what is load-bearing for end users and what is safe to prune.

The anchoring fact:

> **The shipped product reads nothing under `tests/`, `.harness/`, `scripts/`, or `ops/` at
> runtime.** The Python wheel ships only `src/trine_eval/` (hatchling `packages =
> ["src/trine_eval"]`, no package-data); the installed plugin is `plugins/trine-eval/`, and its
> `.harness/` references are instructions for the *target* project, not this repo.

So removing any Tier 2 or Tier 3 path below leaves both the installable wheel and the installed
plugin fully functional for users. "Doesn't break the product" therefore reduces to managing
dependencies *between* the development tiers — see [Removal & breakage](#removal--breakage).

---

## Tier 1 — Product (shipped to users)

Two independent distribution channels.

### A. Claude Code plugin (installed via the marketplace)

| Path | Role |
| --- | --- |
| `.claude-plugin/marketplace.json` | Marketplace manifest — declares the `trine-eval` plugin at `./plugins/trine-eval` |
| `plugins/trine-eval/.claude-plugin/plugin.json` | Plugin manifest — registers skills, agents, hooks |
| `plugins/trine-eval/agents/{planner,generator,evaluator}.md` | The three harness agents |
| `plugins/trine-eval/skills/harness-kickoff/` | Init + planning entry point |
| `plugins/trine-eval/skills/harness-sprint/` | Per-sprint contract→build→eval loop |
| `plugins/trine-eval/skills/harness-summary/` | Cross-sprint analysis |
| `plugins/trine-eval/skills/eval-rubric/` + `rubrics/` | Rubric loader + domain rubrics |
| `plugins/trine-eval/skills/sprint-contract/` + `template.md` | Contract template + protocol |
| `plugins/trine-eval/skills/bootstrap-failures/` + `templates/` | Seed eval suite from real failures |
| `plugins/trine-eval/hooks/hooks.json` | Session/tool lifecycle hooks |
| `plugins/trine-eval/rules/harness-conventions.md` | Authoritative `.harness/` conventions |
| `plugins/trine-eval/scripts/touch-sprint-state.py` | Helper invoked by the PostToolUse hook |

### B. Python library (installed via pip / uv)

| Path | Role |
| --- | --- |
| `src/trine_eval/**` | The full library: `core/`, `judge/`, `models/`, `observability/`, `runner/`, `sandbox/`, plus `cli.py` and `pytest_plugin.py` |
| `pyproject.toml` → `[project]`, `[project.scripts]`, `[project.entry-points.pytest11]`, `dependencies` | Package metadata, the `trine-eval` CLI, the `pytest11` plugin registration, runtime deps |
| `uv.lock` | Lockfile — committed for reproducible installs |

> Packaging note: hatchling ships **only** `src/trine_eval`. Nothing in `tests/`, `.harness/`,
> `scripts/`, or `ops/` enters the wheel, and there are no shipped data files or `py.typed`
> marker.

---

## Tier 2 — Development infrastructure (not shipped; maintained to build & verify the product)

| Path | Kind | Verifies |
| --- | --- | --- |
| `tests/{core,judge,models,observability,runner,sandbox}/` | pytest unit tests | the Python **library** (`src/trine_eval`) |
| `tests/conftest.py`, `tests/__init__.py` | pytest scaffolding | — |
| `tests/smoke/anthropic/test_caching_live.py`, `tests/batch-api-smoke.py`, `tests/playwright-smoke.py` | online smoke tests (creds/probe-gated; SKIP offline) | live API / MCP hookups |
| `tests/verify-runtime-hookups.sh` | standalone shell verifier | harness **methodology** (sandbox isolation, regression abort, transcript schema, audits) |
| `tests/audit-verified-via-command.py` | standalone audit script | adversarial-hygiene of `verified_via_command` flags |
| `tests/generate-audit-report.py` | standalone generator | walks `.harness/evals/`, writes `tests/audit-report.md` |
| `tests/edge-case-aggregate.py` | standalone script | cross-sprint edge-case pass rate (reads the fixture) |
| `tests/check-thinking-frontmatter.py` | standalone checker | plugin agents' `thinking.effort` frontmatter |
| `tests/audit-anthropic-mocked.py` | standalone gate | "no real Anthropic calls in tests" (SN3 gate) |
| `tests/fixture-project/.harness/**` | **test fixture** (hand-authored) | a synthetic sprint-fx/fy harness tree — input for the verifiers above |
| `tests/fixtures/audit-bad/`, `tests/fixtures/calibration/` | test fixtures | inputs for the audit/calibration tests |
| `pyproject.toml` → `[dependency-groups].dev`, `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` | dev tooling config | lint / type-check / test config |
| `scripts/sandbox.sh` | dev convenience | Docker sandbox wrapper |
| `ops/langfuse-compose.yaml` | dev/ops convenience | local Langfuse stack for observability work |

> **Looks like output, is actually a fixture:** `tests/fixture-project/.harness/` resembles
> dogfooding output but is deliberately authored test input (sprint-fx/fy). Keep it with its
> tests.

---

## Tier 3 — Dogfooding / build byproducts (committed, but not part of the shipped product)

| Path | Role | Notes |
| --- | --- | --- |
| `.harness/**` | The build journal of building trine-eval with its own harness (sprints 00–12 + phase-02: spec, contracts, evals, transcripts, regression, progress, summary, planning docs) | Kept as the canonical **worked example**. **Load-bearing caveat:** two Tier-2 verifiers read it — see below. Documented as committed-on-purpose in `CLAUDE.md` and `harness-kickoff/SKILL.md`. |
| `tests/audit-report.md` | Generated output of `tests/generate-audit-report.py` | Its own header says "Generated … on demand." Regenerable; not hand-maintained. |
| `.council/` | henkaten-council governance state | **git-ignored**; an artifact of a *separate* plugin run against this repo, not part of trine-eval. |

---

## Repo meta (neither product nor byproduct)

`README.md`, `CLAUDE.md`, `LICENSE`, `.gitignore` — repository documentation and metadata.

---

## Removal & breakage

Because the product reads nothing in Tiers 2–3, the only constraints on a cleanup are
dependencies *among* the dev/dogfooding paths. The edges that matter:

1. **`.harness/`** is read by `tests/generate-audit-report.py` and
   `tests/verify-runtime-hookups.sh audit-sprint10`. Removing `.harness/` breaks both; remove
   them as a unit.
2. **`tests/audit-report.md`** is generated from `.harness/` by `generate-audit-report.py`. Pure
   output — safe to delete (regenerable while the generator + `.harness/` remain).
3. **`tests/fixture-project/.harness/`** is read by `edge-case-aggregate.py` and
   `verify-runtime-hookups.sh` (regression-abort / transcript-write). Self-contained within
   `tests/`; keep or drop together with those verifiers.
4. **`tests/fixtures/*`** are read by the judge/calibration tests and the
   `audit-anthropic-mocked` self-test. Keep with their tests.
5. **Library unit tests** import `src/trine_eval`. Removing them loses coverage but does **not**
   break the product.
6. **`scripts/sandbox.sh`, `ops/langfuse-compose.yaml`** — nothing imports them.

### Removal candidate sets (increasing aggressiveness)

| Set | Paths | Product impact | Dev-loop impact |
| --- | --- | --- | --- |
| Trivially safe | `ops/`, `scripts/sandbox.sh`, `tests/audit-report.md` | none | none (audit-report.md is regenerable) |
| Drop dogfooding | `.harness/` **+** `generate-audit-report.py`, `audit-verified-via-command.py`, and the `audit-sprint10` / `audit-report` subcommands of `verify-runtime-hookups.sh` | none | loses the worked example + those two audits |
| Drop methodology verification | the standalone verifier scripts **+** `tests/fixture-project/` **+** `tests/fixtures/` (the audit-bad fixture) | none | loses plugin/harness conformance checks |
| **Keep (recommended)** | `tests/{core,judge,models,observability,runner,sandbox}/` | removable, but it is the library's test net | — |

> If the goal is "strip everything that isn't the shipped product," the maximal safe removal is
> all of Tiers 2 and 3 — but that also deletes the library's own test suite and the methodology
> conformance checks. Decide per row above rather than wholesale.
