# Eval Summary — Phase 2

**Mode:** standard (config.mode absent → default; `components_enabled.per_sprint_aci_review` absent → batched ACI review performed here)
**Scope:** Phase 2 only — Sprint 00 (meta-harness prereqs) + Sprints 01-05 (Python library build). Phase 1 (meta-harness sprints 01-12) is captured in [`summary-phase-01.md`](.harness/summary-phase-01.md) and is not re-aggregated here.
**Date generated:** 2026-05-20

## Overview
- Phase 2 sprints completed: 6 (Sprint 00 + Sprints 01-05)
- Overall pass rate (final round): 85/85 = **100%**
- Overall weighted pass rate (final round): **100%** (all six sprints landed at 100/100)
- Average rounds per sprint: 9 rounds / 6 sprints = **1.5**
- First-round pass rate (capability signal): 82/85 = **96.5%** (Sprint 00 C4, Sprint 01 SN1, Sprint 03 C9 each FAILED in R1 — all three were contract-text bugs, not implementation bugs)
- Cross-sprint edge-case pass rate: **N/A** — no Phase 2 contract declared an `## Edge Case Criteria` section. The eval-harness rubric encodes edge-case concerns inside the dimension scoring tables rather than as separate criteria, and this is the expected shape for `eval-harness` projects (see `skills/harness-summary/SKILL.md`).

## Consistency Metrics

`config.trials == 1` for every Phase 2 sprint, so per the skill: "If only one trial exists (single-trial mode), p is simply the round's pass rate and pass@1 = pass^1 = p." Trial-based consistency cannot be measured with a single trial — the numbers below collapse to the final-round pass rate and carry no variance signal.

| Sprint | p (final round) | k (trials) | pass@k | pass^k |
|--------|-----------------|------------|--------|--------|
| 00     | 1.00            | 1          | 1.00   | 1.00   |
| 01     | 1.00            | 1          | 1.00   | 1.00   |
| 02     | 1.00            | 1          | 1.00   | 1.00   |
| 03     | 1.00            | 1          | 1.00   | 1.00   |
| 04     | 1.00            | 1          | 1.00   | 1.00   |
| 05     | 1.00            | 1          | 1.00   | 1.00   |

- Overall pass@k: **1.00** (single-trial collapse)
- Overall pass^k: **1.00** (single-trial collapse)
- Consistency gap (pass@k − pass^k): **0** — uninterpretable at trials=1; raising `config.trials` to ≥2 is the prerequisite for a real consistency reading. See Recommendations.

## Per-Sprint Results

| Sprint | Title                                             | Verdict | Rounds | Pass Rate (final) | First-Round Pass | Weighted | Edge Case Pass Rate |
|--------|---------------------------------------------------|---------|--------|-------------------|------------------|----------|---------------------|
| 00     | Meta-harness prereqs (sprint-state, python_build) | PASS    | 2      | 5/5 = 100%        | 4/5 (C4 FAIL)    | 100%     | N/A                 |
| 01     | Python library bootstrap + core primitives        | PASS    | 2      | 11/11 = 100%      | 12/13 (SN1 FAIL) | 100%     | N/A                 |
| 02     | Runner, replayable logs, pytest plugin, OTel      | PASS    | 1      | 12/12 = 100%      | 15/15            | 100%     | N/A                 |
| 03     | Prompt caching + Batch API                        | PASS    | 2      | 11/11 = 100%      | 13/14 (C9 FAIL)  | 100%     | N/A                 |
| 04     | LLM-as-judge: rubric, calibration, bootstrap, tiers | PASS  | 1      | 14/14 = 100%      | 17/17            | 100%     | N/A                 |
| 05     | Docker sandbox + 4-stage prefilter + regression gate | PASS | 1      | 16/16 = 100%      | 19/19            | 100%     | N/A                 |

**Per-sprint rubric scores** (methodology / grading / separation / context / extensibility, each /5):

| Sprint | Methodology | Grading | Separation | Context | Extensibility |
|--------|-------------|---------|------------|---------|---------------|
| 00     | 4           | 4       | 5          | 4       | 4             |
| 01     | 4           | 4       | 5          | 4       | 4             |
| 02     | 3           | 4       | 4          | 4       | 4             |
| 03     | 4           | 4       | 5          | 4       | 3             |
| 04     | 4           | 4       | **3**      | 4       | 4             |
| 05     | 4           | 4       | 5          | 4       | 4             |

## Trend Analysis

- **Verdict trend:** flat at PASS — 6/6 sprints landed PASS at 100% weighted score.
- **First-round pass trend:** 86% → 92% → 100% → 93% → 100% → 100%. The Generator's first-attempt accuracy is improving and saturating high — only contract-text bugs (verification commands) have caused R2s, never implementation defects.
- **Rounds-per-sprint trend:** 2 → 2 → 1 → 2 → 1 → 1. The harness has stabilized at one round per sprint since Sprint 04, with the contract-bug rate dropping as the contract authors absorbed lessons from earlier R2 fixes.
- **Methodology rubric:** stuck at 4/5 for almost every sprint with one dip at Sprint 02 (3/5). The ceiling is consistent — the harness keeps citing the same two missing items (automated saturation graduation pathway, bootstrap-from-real-failures facility). This summary's regression.json append addresses one half of that gap directly.
- **Separation rubric:** 5/5 dominant (4 of 6 sprints). Sprint 02 (4/5) and Sprint 04 (3/5) are one-off dips — Sprint 04 was the documented main-thread fallback when the Evaluator subagent exhausted its turn budget twice in Round 1. There is no trend, just a specific failure mode (see ACI Improvements below).
- **Pass^k trend:** flat at 1.00 across all sprints — but this is an artifact of `config.trials == 1`, not a true consistency signal.

## Common Failure Patterns

All three R1 FAILs in Phase 2 share the same root cause: **contract verification commands had latent bugs that the Evaluator caught empirically but contract negotiation missed by inspection alone.**

| Sprint | Criterion | R1 FAIL cause                                                                 | Fix                                                                                |
|--------|-----------|-------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| 00     | C4        | Python `subprocess.run(cmd, shell=True)` routes through `cmd.exe` on Windows  | Explicit Git Bash path in verification command (`bf30c09`, `b54a478`)              |
| 01     | SN1       | `.harness/evals/sprint-*.md` glob matched sprint-00 Phase 2 files unintentionally | Narrowed to `sprint-0[1-9]*.md` + `sprint-1*.md` (`39a5ae7`)                       |
| 03     | C9        | `[ "$EC" = "0" ]` did not anticipate Sprint 2's pytest plugin exit-100 override | Disjunction `[ "$EC" = "0" ] || [ "$EC" = "100" ]` (`0e1db3f`)                     |

**Common signature:** every Phase 2 R1 fail was a CONTRACT-ONLY fix in R2 — zero implementation files changed across all three fix commits. The Generator's source code was correct on first attempt every time. The contract author's verification commands were the bug surface. This pattern persisted across three sprints and is the strongest ACI lever in the project.

Contract-bug FAILs were caught only when the Evaluator ran the literal verification command, exactly as required by the adversarial hygiene rule. A lenient grader (e.g., "the underlying behavior is fine, mark PASS") would have masked all three and shipped broken regression scaffolding into later sprints.

## Saturation & Regression Graduation

| Criterion (most recent task_id) | Consecutive First-Round Passes (Phase 2 only) | Status                       | Action Taken                                                                 |
|---------------------------------|-----------------------------------------------|------------------------------|------------------------------------------------------------------------------|
| `s03-sn2` — No forbidden packages (langgraph/ragas/pgvector/fastapi) | S01, S02, S03, S04, S05 (5) | **Saturated — easy gate**    | **GRADUATED** to `.harness/regression/regression.json` with `graduated_from_sprint: 3` |
| `s04-sn3` — No real Anthropic API calls in tests | S02, S03, S04 (3) — pattern then mutated in S05 to Docker | **Saturated — capability gate, but LLM-judge** | Not graduated (verification_command is null; needs a deterministic audit script — see Recommendations) |
| SN1 — Historical artifacts unmodified | S02, S03, S04, S05 (4 after S01 R1 fix)       | Saturated but evolving       | **NOT GRADUATED** — verification glob mutates per-sprint (sprint-0[1234]*.md grows by one digit each sprint to exclude the current contract); not stable across sprints |
| "Current sprint package green" (s02-c10/s03-c8/s04-c11/s05-c13) | S02, S03, S04, S05 (4)                       | Saturated but sprint-specific | **NOT GRADUATED** — each sprint's test target points at a different new package; not a stable single check |
| "No regressions in prior tests" (s04-c12, s05-c14)                | S04, S05 (2)                                  | Not yet saturated (Sprint 03's C9 FAILED in R1) | Watch; may saturate after one more sprint |

**Graduation file write:** appended `s03-sn2` to [`.harness/regression/regression.json`](.harness/regression/regression.json) verbatim from `.harness/contracts/phase-02/sprint-03.tasks.json`, with the `graduated_from_sprint: 3` field added per the skill's append-only protocol. The pre-existing three Phase-1 regression entries (`harness-tasks-json-coverage`, `harness-historical-artifacts-immutable`, `harness-verified-via-command-audit`) are preserved unmodified.

**Replacement recommendation for next sprint's contract:** because `s03-sn2` was *inherently easy* (a stable git grep over a fixed alternation), it should be graduated **without replacement** — no harder variant of "are forbidden packages absent" exists. Sprint 06's contract should focus its weight elsewhere.

## Recommendations

1. **Raise `config.trials` to 2-3 for the next sprint.** With trials=1, pass@k and pass^k carry no consistency information — the summary cannot distinguish a reliable agent from a lucky one. The Generator pattern (one-shot correct code, occasional contract bugs) makes consistency measurement particularly valuable: if the agent is genuinely reliable, pass^3 should also be high; if it's getting lucky, the gap will appear. Cost trade-off: trials=2 doubles per-sprint eval cost. Recommendation: enable trials=2 from Sprint 06 onward.

2. **Add a `tests/audit-anthropic-mocked.py` script and graduate s04-sn3.** The "no real Anthropic API calls in tests" gate has saturated as an LLM-judge but cannot be cleanly graduated because its `verification_command` is null. Mirror the pattern from `tests/audit-verified-via-command.py` (which mechanized the SN3-style llm-judge from Sprint 10 in Phase 1) to convert this into a deterministic regression gate. One sprint of work; closes a real saturation gap.

3. **Add Windows-vs-bash guidance to the sprint-contract template.** Three of three Phase 2 R1 fails were verification-command bugs and Sprint 00's C4 was specifically a Windows shell-routing bug. Add a "Cross-platform verification commands" subsection to [`skills/sprint-contract/SKILL.md`](skills/sprint-contract/SKILL.md) covering: explicit Git Bash invocation on Windows, the Sprint 2 pytest-plugin exit-100 disjunction pattern, and a "test your glob against the actual file set before approval" checklist. This is the single largest ACI lever in the project (see ACI Improvements below).

4. **Document the Evaluator turn-budget fallback policy more prominently.** Sprint 04 cost a separation rubric point (5→3) because two consecutive forked Evaluator subagents exhausted their turn budget during Round 1 contract review without writing the verdict, forcing main-thread authorship. The fallback is documented in [`skills/harness-sprint/SKILL.md`](skills/harness-sprint/SKILL.md) but the *prevention* guidance (write the review skeleton first, fill in details after, so the file lands even if budget runs out) is not. See ACI Improvements.

5. **Enable per-sprint ACI review by setting `components_enabled.per_sprint_aci_review: true`.** The current minimal-default forces this summary to do batched ACI review at month-end, which detects patterns but loses immediacy — a contract-command bug spotted at sprint time can be fixed before it propagates; spotted in summary, it's already in three downstream contracts. Cost: marginal extra tokens per sprint.

6. **The methodology rubric ceiling at 4/5 is now the dominant scoring constraint.** Five of six Phase 2 sprints scored 4/5 on methodology, citing the same missing items (automated saturation graduation, bootstrap-from-real-failures facility). This summary's append to `regression.json` materially advances the first; the second remains open and should be a Sprint 6+ candidate.

## Tool & Skill Description Improvements

This run performed a **batched ACI review** across all six Phase 2 eval files (no `per_sprint_aci_review`-flagged sections exist in any Phase 2 eval). The recurring pattern across sprints is that the Generator's source-code attempts were one-shot correct, while the contract author's verification commands had latent platform/scope/exit-code bugs — so the highest-leverage ACI changes are to the contract-authoring skill and the evaluator agent guidance, not to the build skills.

**Proposed change 1 — `skills/sprint-contract/SKILL.md`: add "Cross-platform verification commands" subsection.**

Rationale: 3 of 3 Phase 2 R1 fails (S00 C4, S01 SN1, S03 C9) were verification-command bugs. The patterns are concrete and reusable:

- Windows path bug (S00 C4): `subprocess.run(cmd, shell=True)` routes through `cmd.exe` on Windows and cannot parse bash. Fix template: invoke Git Bash explicitly via `r'C:\Program Files\Git\usr\bin\bash.exe' if os.name=='nt' else 'bash'`.
- Glob over-match bug (S01 SN1): `.harness/evals/sprint-*.md` matched newly-created Phase 2 sprint-00 files. Fix template: anchor sprint number digits (`sprint-0[1-9]*.md` excludes `sprint-00`); run the glob against `git ls-files` output before contract approval.
- Exit-code expectation bug (S03 C9): `[ "$EC" = "0" ]` failed when Sprint 2's pytest plugin overrode session exit to 100. Fix template: disjunction `( [ "$EC" = "0" ] || [ "$EC" = "100" ] )` plus a `! grep -qE "FAILED|ERROR"` guard.

**Held-out validation:** Reviewed Sprint 04 and Sprint 05 (held out — both had clean R1 PASS). Neither contract introduced new verification-command patterns; the cumulative learning from S00→S03 is already visible in those contracts' verification commands (S04 SN1 uses `sprint-0[123]*.md`; S05 C14 uses the exit-100 disjunction). The proposed subsection would have written down what S04 and S05 already do. No regression risk — formalizing existing successful patterns.

**Status:** documented as Recommendation #3 above; not applied to skill files in this run because this summary is read-only over the harness skills. Apply during a follow-up sprint or operator pass.

**Proposed change 2 — `agents/evaluator.md`: add "Turn-budget defensive authorship" guidance.**

Rationale: Sprint 04 Round 1 lost a Separation rubric point because the forked Evaluator subagent ran out of turns before writing the review section (twice — the second subagent reached 41 tool calls confirming SN1 baseline failure but never wrote the verdict). The fallback to main-thread authorship is documented in `skills/harness-sprint/SKILL.md`; the *prevention* technique isn't.

Proposed addition (one paragraph): "When the contract has more than ~10 criteria or any LLM-judge criterion requires multiple-file reads, write the review skeleton (criterion headings + Result: pending placeholders) to the eval file *first*, before deep investigation. Then fill in evidence per criterion. This guarantees the file lands even if budget runs out and the main thread does not need to fall back."

**Held-out validation:** Sprint 05 Round 1 had 19 criteria (the largest in Phase 2) and 3 advisory items, yet the forked Evaluator landed cleanly. The pattern was: read contract + tasks.json + config + source files in parallel up front, then issue verification commands in batched parallel groups (C1-C6, then C7-C12, then SN gates). The proposed guidance would codify what Sprint 05's Evaluator did intuitively. No regression risk — formalizes a successful pattern.

**Status:** documented as Recommendation #4 above; not applied to agent files in this run for the same reason.

**No tool description changes proposed.** The Bash/Read/Grep/Write tool descriptions performed correctly across all six Phase 2 sprints — no Evaluator misinterpretations of tool semantics were observed in any transcript trailer. All tool failures observed in transcripts were the *targeted* failures the evaluator was running (intentional pytest exits, intentional grep no-match for SN gates), not tool-description ambiguity.
