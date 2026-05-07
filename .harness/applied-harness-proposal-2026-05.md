# Applied Harness Proposal: Validate trine-eval Against a Real Consumer Project

**Date:** 2026-05-01
**Status:** Proposed (Phase 3 plan, post-Sprint-12)
**Author:** Synthesized from Sprint 12 cross-sprint summary recommendations

## Why This Exists

Phase 2 (Sprints 6–12) closed all 10 playbook gaps from `.harness/playbook-alignment-2026-04.md`. Every gap is end-to-end live in offline mode: trial loop, sandbox, regression suite, transcript capture, edge-case taxonomy, Playwright dispatch, Batch API protocol, adversarial hygiene, adaptive thinking, formal task taxonomy. The cross-sprint summary at `.harness/summary.md` reports 100% pass rate, 100% weighted score, 5/5 across four of five rubric dimensions — and a permanent caveat that **the meta-eval cannot exercise the metrics it ships**:

- `pass@k` / `pass^k` are degenerate at `trials == 1`. Sprint 11's fixture project ran `trials: 3` against a deterministic command (`test -s ...`), so `p = 1.0` collapsed the consistency gap. **No statistically valid consistency measurement exists at the parent level.**
- **Edge Case Pass Rate is N/A** across all 12 parent sprints — the meta-eval delivers config/protocol changes, not input-handling code where edge cases produce signal.
- **Live external-service paths (Batch API HTTP, Playwright MCP) are protocol-shipped only.** Sprint 12 verified them offline with `[SKIP]`-on-absence semantics; the live paths have never run.

The next signal upgrade requires applying the harness to a non-meta-eval consumer project. The plan below is three escalating paths from "least friction, validates the mechanics" to "full validation, exercises every Phase 2 gap end-to-end against live infrastructure."

## Path A — `cli-tool` Consumer (lowest friction, ~1 day, ~$5–20)

Pick a small CLI utility (markdown linter, JSON formatter, a `git` helper). Apply the harness as a 3-sprint plan.

**Sprint A1 — initialization.** `/trine-eval:harness-kickoff` against the CLI repo. Expected outcome: harness initialized, `config.json` set to `project_type: "cli-tool"`, rubric loaded, `sprints.json` proposes 3–5 sprints. *No edge-case slot* (the rubric guidance correctly skips edge-case proposals for `cli-tool`). **What this validates:** kickoff works against a non-meta-eval project.

**Sprint A2 — first feature build.** Pick the smallest feature in `sprints.json` and run `/trine-eval:harness-sprint`. **What this validates:** end-to-end Generator/Evaluator separation against a real project. The forked-context Evaluator now has `Write` (Sprint 12 C1), so eval emission is direct — no main-thread fallback.

**Sprint A3 — Batch API live submission.** Set `config.batch.enabled = true`, `config.batch.min_criteria = 3`. Set `ANTHROPIC_API_KEY`. Run `/trine-eval:harness-sprint`. The harness should detect criterion count ≥ `min_criteria`, submit a batch via `/v1/messages/batches`, poll, demultiplex by `custom_id`. **What this validates:** Gap 7 end-to-end against a live endpoint. Sprint 12 verified the request shape offline; this verifies actual HTTP submission, polling, and result-mapping.

**Failure modes to watch:** polling-timeout handling, rate limits, partial-success demuxing.

## Path B — `web-app` Consumer (medium friction, ~1 week, ~$30–100)

Pick a small web app (TODO list, markdown previewer, kanban board — frontend + small backend). Initialize as `project_type: "web-app"`. Adds Playwright invocation on top of Path A.

**Sprint B1 — initialization with edge-case proposals.** The rubric guidance for `web-app` proposes edge-case criteria automatically: viewport extremes (320px and 4K), keyboard-only navigation, JavaScript disabled, max-length input, empty form submissions. Expected outcome: contract for the first sprint includes a non-empty `## Edge Case Criteria` section. **What this validates:** edge-case proposals fire for `web-app` (Sprint 10 protocol).

**Sprint B2 — Playwright invocation.** Confirm `evaluator_tools.playwright = "auto"`. Drop the probe file (`touch tests/.playwright-available`). The Evaluator should detect Playwright availability and use `mcp__claude-in-chrome__*` (or equivalent) to drive the rendered DOM during eval. **What this validates:** Gap 9 end-to-end. Sprint 12 verified the protocol-level dispatch (probe-file + python-package import); this exercises actual browser navigation against a real DOM.

**Sprint B3 — edge-case pass rate aggregation across two sprints.** Once two sprints with edge-case criteria have run, `harness-summary` should compute the cross-sprint aggregate via the Sprint 12 formula. Expected outcome: `Cross-sprint edge-case pass rate: P/T = X%` appears in `summary.md`'s Overview. **What this validates:** Gap 8 end-to-end at the parent level (Sprint 12 only validated against the synthetic `sprint-fx`/`sprint-fy` fixture pair).

**Failure modes to watch:** Playwright MCP integration assumes a working browser-automation toolchain; if the Claude Code instance can't drive a real browser, this stalls. Fallback to curl-based Visual Design grading (documented in `agents/evaluator.md`).

## Path C — `rag-system` Consumer (highest friction, ~2 weeks, ~$100–500)

Pick or build a small RAG pipeline (10–50 documents, vector store, LLM-driven query path). Initialize as `project_type: "rag-system"`. The most exercise of LLM-judge criteria, and therefore the most exercise of the consistency metrics that have been degenerate across the meta-eval.

**Sprint C1 — multi-trial consistency measurement.** Set `config.trials = 3` (Sprint 6's default-1 changed for the first time at the parent level). Pick a sprint criterion that's LLM-judged and inherently non-deterministic (e.g., "the system declines to answer when the corpus contains no relevant documents" — judged by reading the response). The harness emits 3 trial files: `sprint-CN-r1-t{1,2,3}.md`. The Evaluator runs the same code at the same git head against each. Expected outcome: pass@3 / pass^3 are non-trivial — the consistency gap signal becomes visible for the first time. **What this validates:** Gap 1 end-to-end with non-deterministic p. Sprint 11's fixture had p=1.0 (deterministic), so the gap collapsed. This sprint exercises real LLM non-determinism.

**Sprint C2 — citation hallucination edge case.** The `rag-system` rubric proposes citation hallucination on out-of-corpus queries as an edge case. Build the criterion, evaluate, observe whether the agent passes the obvious case (answer in corpus) but fails the adversarial case (made-up question demanding a citation). **What this validates:** edge-case asymmetry — a sprint that scores 100% weighted but, say, 30% on edge cases. This is the failure mode the Edge Case Pass Rate metric was designed to surface.

**Sprint C3 — saturation graduation in the wild.** After 3+ RAG sprints, run `/trine-eval:harness-summary`. Saturation detection should identify any criterion-type that passed first-round across all 3 sprints; graduate the saturated patterns into the consumer project's `regression.json`. **What this validates:** the saturation→graduation pipeline works end-to-end against a real project (Sprint 12 only validated it against meta-eval invariants).

**Failure modes to watch:** highest LLM-judgment exposure means the most chances for grader disagreement. Watch the `## Human Review Flags` section in each eval — the calibration touch-points where human spot-check matters most.

## Recommended Sequence

**Start with Path A.** It exercises the full Generator/Evaluator/contract-negotiation loop against a real project for the first time, validates the post-Sprint-12 cache state (Write tool, authoring checklist, evaluator-fallback documentation), and verifies Batch API end-to-end at low cost.

If Path A succeeds, escalate to Path B for Playwright + edge cases, then Path C for non-deterministic consistency measurement.

## Pre-Flight Checklist (post-Sprint-12)

Before starting any path:

- [ ] Plugin cache reflects post-Sprint-12 source. The 0.3.1 version bump (this commit chain) and a `/plugin update trine-eval` (or equivalent reinstall) are the supported refresh path. The Sprint 12 manual cache sync at `~/.claude/plugins/cache/trine-eval/trine-eval/0.3.0/` is a development-mode workaround that may be overwritten on the next plugin update.
- [ ] `agents/evaluator.md` `tools:` line includes `Write`. Verify with `awk '/^---$/{c++; next} c==1' agents/evaluator.md | grep -E '^tools:.*Write'`.
- [ ] `regression.json` carries the 3 graduated invariants (`harness-tasks-json-coverage`, `harness-historical-artifacts-immutable`, `harness-verified-via-command-audit`). Step 0.5 will run them before the first sprint.
- [ ] `ANTHROPIC_API_KEY` is set in the environment if Path A is the goal.
- [ ] For Path B/C: a working `mcp__claude-in-chrome__*` toolchain is connected (Path B only).

## Open Questions

1. **Cost containment for Path C.** A 3-trial budget on every sprint is the dominant cost driver; Sprint C1's design assumes the operator accepts ~3× per-eval cost for the Phase 2 consistency signal. Consider: should `config.trials` apply only to LLM-judge criteria, with deterministic criteria running once per round? This is a future enhancement, not a Sprint-12-blocker.

2. **Sprint-state.json gap.** The single sub-5 dimension in Sprint 12 is Context (4/5), driven by the missing `.harness/sprint-state.json` file. A small follow-up sprint could close it before Path A — or it could be folded into the first applied-harness initialization (kickoff would write the file fresh).

3. **Re-running the playbook gap analysis.** All 10 gaps are end-to-end live offline. A `playbook-alignment-2026-05.md` file (modeled on `playbook-alignment-2026-04.md`) would confirm 5/5 across the 8-step playbook against the post-Sprint-12 state. Recommended before Path C, optional before Path A/B.

## How This File Is Used

When you next sit down to update or extend `trine-eval`, this file is the entry point:

- It captures the *next concrete experiments* the harness needs in priority order.
- It captures the *cost shape* of each path so the choice is informed.
- It captures the *pre-flight checklist* so a path doesn't fail on a missed prerequisite.
- It is **append-only by convention** — Phase 3 results, applied-harness deltas, and follow-up proposals should be added below this section, not edited inline.

If you start one of these paths, update the Status field at the top of this file and add a `## Path X Results` section below as evidence accrues. Treat this proposal the way Sprint 12 treated `playbook-alignment-2026-04.md` and `gap-closure-plan-2026-04.md`: a planning doc that becomes audit history once the work lands.
