---
paths: .harness/**
---

# Harness Conventions

- Sprint contracts are the source of truth for what "done" means
- JSON files in `.harness/` use 2-space indentation
- Eval results must include specific evidence for every FAIL grade
- Never modify a prior sprint's eval results — they are append-only records
- Communication between agents happens exclusively via files in `.harness/`
- The Evaluator never sees the Generator's reasoning trace

## JSON vs Markdown: When to Use Each

The harness uses two file formats for distinct purposes:

- **JSON** — Machine-readable structured state. Use for: `config.json`, `sprints.json`, `sprint-state.json`. JSON is preferred for structured data because models are less likely to inappropriately modify it during edits. JSON files are the source of truth for sprint status, configuration, and machine-parseable results.
- **Markdown** — Human-readable prose and notes. Use for: `progress.md`, `spec.md`, sprint contracts, eval reports. Markdown is better for session logs, design rationale, and any content that benefits from rich formatting.

Both formats should be kept in sync where they overlap (e.g., sprint status appears in both `sprint-state.json` and `progress.md`). When they conflict, JSON is authoritative for structured state.

## Trial vs Retry

The harness has two independent loops that are easy to confuse — and conflating them produces statistically invalid pass@k / pass^k, because a fixed bug starts looking like evidence of inconsistency.

- **Trial** — A measurement run at **fixed code state**. Trials exist to estimate how reliable the current implementation is. Multiple trials are independent samples of the same agent doing the same task, differing only in trial-time non-determinism (model stochasticity, timing, sandbox entropy). Trials are controlled by `config.trials` (default `1`). Files: `sprint-NN-rR-tT.md`, where `T` is the trial index within round `R`. When `trials == 1`, the `-tT` suffix is omitted and the file is `sprint-NN-rR.md` (Phase 1 backward compatibility).
- **Retry** — A **bug-fix iteration**. Retries exist to let the Generator edit code in response to Evaluator feedback. Code changes between retries; trial counts do not need to. Retries are controlled by `config.max_retries`. Files: the round counter `R` increments with each retry.

Pass@k and pass^k are computed from trial files only (see `skills/harness-summary/SKILL.md`). Retry-round pass rates remain useful as a separate `first-round-pass` / retry-efficiency signal, but they are not a valid consistency metric.

## tasks.json Schema

After contract approval, `.harness/contracts/sprint-NN.md` is accompanied by a sibling `.harness/contracts/sprint-NN.tasks.json`. This is the machine-readable source of record for the sprint's criteria — Sprint 7's regression gate, Sprint 8's Batch API scheduler, Sprint 9's transcripts, and Sprint 10's adversarial hygiene flags all key off it.

Fields:

- `task_id` — Stable id. `s<NN>-c<N>` for scored success criteria, `s<NN>-sn<N>` for Should-NOT gates. Downstream tools reference tasks by this id across trials and sprints, so it must not be renamed after approval.
- `criterion` — Verbatim criterion text copied from the markdown contract. No paraphrasing.
- `grader_type` — `"deterministic"` or `"llm-judge"`.
- `weight` — Integer percentage. Success criteria carry the weights declared in the markdown contract (summing to 100%); gate criteria use `0` because they are not weighted.
- `is_gate` — `true` for Should-NOT gates, `false` otherwise.
- `verification_command` — Runnable shell command for deterministic criteria; `null` for llm-judge.
- `rubric_dimension` — Which rubric dimension this criterion informs. Used for per-dimension summary rollups.

Emission is guarded by `config.taxonomy.emit_tasks_json` (default `true`). See `skills/sprint-contract/SKILL.md` for the full specification and an example.

## regression.json Schema and Gate Semantics

`.harness/regression/regression.json` is the append-only graduation output of the harness's saturation detection. It is **not** a hand-curated list — `skills/harness-summary/SKILL.md` appends entries to it as criteria saturate (first-round-pass across 3+ consecutive sprints), and `skills/harness-sprint/SKILL.md` Step 0.5 reads it on every sprint to gate new contract negotiation.

**Role.** `regression.json` is the downstream product of a single pipeline: sprint contracts → `tasks.json` → saturation detection → `regression.json` → Step 0.5 gate. Entries are copied verbatim from the producing sprint's `.harness/contracts/sprint-NN.tasks.json`, so every field a regression runner needs is already calibrated by the contract negotiation that produced it.

**Schema.** Each entry in the top-level `tasks` array carries the same fields as a `tasks.json` entry — `task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension` — plus one added field:

- `graduated_from_sprint` — Integer. The sprint number whose eval first demonstrated saturation (typically the 3rd consecutive first-round-pass sprint). Used for audit trails: every regression failure is traced back to the sprint that justified adding the entry.

No fields from `tasks.json` are renamed or dropped. The added field is the only Sprint-7 schema extension.

**Append-only.** The harness never removes or rewrites existing entries. A buggy summary run could otherwise destroy historical regression coverage in a single write; the append-only rule makes graduation loss impossible by construction. Operators who want to retire a regression criterion do so by hand, outside the harness.

**Gate semantics.** `skills/harness-sprint/SKILL.md` Step 0.5 runs every entry's `verification_command` — verbatim, with no paraphrase — before contract negotiation for a new sprint. Each task's PASS (exit 0) or FAIL (non-zero) verdict is recorded to `.harness/regression/runs/run-<UTC-ISO8601>.json`. If any task fails and `config.regression.fail_fast` is true (default), the sprint aborts with the failing `task_id` and `graduated_from_sprint` so the operator knows which capability regressed. The gate is `fail_fast` by default because a new sprint's criteria are independent of prior capabilities — the new eval can grade PASS on fresh work while a graduated capability has silently broken, and shipping that green score would overstate system health.

**Backward compatibility.** If `regression.json` does not exist, or its `tasks` array is empty, or `config.regression.enabled` is explicitly `false`, Step 0.5 is a no-op. Projects that predate Phase 2 and never graduate a criterion experience no behavior change.

## Transcript Schema

Each evaluator run produces an optional structured JSON transcript at `.harness/transcripts/sprint-NN-rR-tT.json` (multi-trial mode) or `.harness/transcripts/sprint-NN-rR.json` (single-trial mode, the default). The transcript is the machine-readable sibling of the markdown eval at `.harness/evals/sprint-NN-rR-tT.md` — same naming, different format, paired 1:1.

**Role.** Transcripts are the audit-grade record of the Evaluator's behavior across runs: which tools it called, what messages were exchanged, how much it spent on tokens and time, and a one-paragraph summary of how it reasoned. The harness-summary skill links the transcript path next to FAIL criteria and grader-disagreement entries so a human auditor can trace the verdict back to ground truth — see `skills/harness-summary/SKILL.md`. Transcripts are an audit artifact, not a grading input.

**Pipeline.** Evaluator emits markdown eval ending with a fenced JSON code block under a `## Transcript Trailer` section → `skills/harness-sprint/SKILL.md` Step 3e reads the markdown, extracts the trailer block, parses it as JSON → writes the parsed JSON verbatim to `.harness/transcripts/sprint-NN-rR-tT.json`. The trailer instruction itself lives in `agents/evaluator.md` under **Transcript Trailer (Structured Output)**. If the section is missing or the JSON malformed, the workflow skips the write rather than failing the eval — transcripts are append-only-when-available, never forced.

**Schema.** Top-level keys (all required, except runtime-instrumented fields documented as nullable):

- `"sprint"` — Integer. The sprint number this run graded.
- `"round"` — Integer. Round 1 for the initial eval, R+1 for retry round R.
- `"trial"` — Integer. 1 for single-trial mode, otherwise the 1..config.trials index within the round.
- `"messages"` — Array of `{role, content}` objects summarizing the message exchange. May be a high-level summary when the full message array is not directly available to the agent. Empty array `[]` is permitted when no summary is feasible.
- `"tool_calls"` — Array of `{name, arguments_summary, result_summary}` objects, one per tool call the Evaluator made. Each summary is one-line; the field is the ground truth Sprint 10's adversarial-hygiene checks key off.
- `"token_usage"` — Object `{input, output, cache_hit}` with integer or `null` values. **Runtime-supplied. The Evaluator must write `null` rather than fabricating values when the runtime does not expose token counts.** Fabricated counts contradict the calibration purpose of transcripts.
- `"timing"` — Object `{ttft_ms, total_ms}` with integer or `null` values. **Runtime-supplied per the same rule as `token_usage`. `null` allowed; fabrication forbidden.**
- `"thinking_summary"` — String. The Evaluator's one-paragraph summary of its reasoning approach. Captures Sprint 8's adaptive-thinking output that would otherwise be lost when only the markdown eval is preserved.

The schema is intentionally extensible. Sprint 10 will add `verified_via_command` per-tool-call adversarial-hygiene flags inside `tool_calls` entries (or as a top-level array) without renegotiating these top-level fields.

**Why each field exists.** `messages` because reading the actual model output is the only way to verify a grader's reasoning chain across runs; `tool_calls` because adversarial-hygiene checks need to confirm a verification command actually ran; `token_usage` because cost regressions are otherwise invisible; `timing` because slow evals correlate with grader confusion; `thinking_summary` because the adaptive-thinking declaration from Sprint 8 produces internal reasoning that is otherwise lost when only the markdown eval is preserved. The runtime-nullable design for `token_usage` and `timing` reflects that the evaluator agent typically cannot observe its own runtime instrumentation directly — better an honest `null` than a fabricated number.

**Configuration.** Two knobs gate transcript behavior, both with backward-compatible defaults:

- `config.transcripts.capture` — Boolean. Default `true` when the `transcripts` object is present in `.harness/config.json`. When `true`, Step 3e attempts trailer extraction. When `false`, Step 3e is skipped entirely and no transcript files are written. When the `transcripts` object is absent (legacy/Phase-1 config), the Phase-1 default applies — see Backward Compatibility below.
- `config.transcripts.retain_days` — Integer. Default `30`. Declared retention window. Cleanup is policy-only in Sprint 9; actual deletion of files older than this threshold runs out-of-band or in a future sprint. Note that summary graduation needs at least 3 sprints of evidence, so the retention window must be long enough to cover the saturation-detection lookback (see `skills/harness-summary/SKILL.md`).

**Backward compatibility.** A project whose `.harness/config.json` lacks the `transcripts` object and whose `agents/evaluator.md` predates Sprint 9 experiences no functional behavior change. The legacy evaluator does not emit a `## Transcript Trailer` section, so Step 3e's failure-tolerant extraction falls into the no-op branch and no transcript file is written. The `capture: true` default applies to fresh installs that pick up the updated agent file (which then start emitting trailers); for legacy installs, Phase-1 disk state is preserved. End-to-end transcript writing against a live evaluator subagent is deferred to a synthetic verification sprint per the gap-closure plan, matching Sprint 8's posture for `thinking.profile` — Sprint 9 ships the protocol and the schema, not a forced runtime hookup.

**Failure-tolerant extraction.** If the markdown eval lacks a `## Transcript Trailer` section, the fenced code block is malformed, or the parsed JSON is missing required top-level fields, Step 3e skips the write rather than failing the eval. Transcripts are an audit artifact, not a grading input — losing one for a single run does not invalidate that run's verdict. This matches Sprint 7's append-only stance for regression entries: the harness never destroys evaluator output to "fix" a missing transcript.

## Edge Case Criteria

Sprint contracts may declare an optional `## Edge Case Criteria` section, distinct from the 100%-weighted Success Criteria and from Should-NOT gates. Edge cases test ambiguous, boundary, or adversarial inputs (empty inputs, oversized payloads, concurrent requests, queries with no matches). They are tracked separately as **Edge Case Pass Rate** in `harness-summary` and **do not contribute weight** to the Success Criteria total — so omitting the section does not break the weight-sum-to-100% invariant.

**Why a third class.** Folding edge cases into the weighted total is the one-sided-eval failure mode the playbook calls out: an agent that passes only obvious positive cases would earn the same weighted score as one that also handles ambiguous cases. Reporting Edge Case Pass Rate as its own metric makes the asymmetry visible — a sprint at 100% weighted with 30% edge-case pass rate has a materially different story than 100%/95%.

**When to include.** Most valuable for `web-app`, `api-service`, and `rag-system` rubrics — those domains have well-known edge-case boundaries that the rubric's dimension scoring tables alone do not cover at sufficient granularity. For `cli-tool` and `eval-harness` deliverables, the rubric's existing dimensions usually cover the relevant edge-case concerns and the Evaluator may skip the recommendation.

**Schema.** Edge case criteria appear in `tasks.json` with `is_gate: false`, `weight: 0` (they do not contribute weight), and an optional `is_edge_case: true` flag, so the harness-summary computer can split edge-case results from weighted Success Criteria results without parsing the markdown contract. The flag is additive — Sprint 1–9 entries do not carry it and continue to grade as Success Criteria. See `skills/sprint-contract/SKILL.md` for the contract-author-facing rationale and per-rubric guidance.

**Backward compatibility.** Sprint contracts that predate Sprint 10 do not declare `## Edge Case Criteria`. Their `tasks.json` files contain only Success Criteria and Should-NOT entries, exactly as before. The Edge Case Pass Rate metric in summary output is rendered as `N/A` when no sprint declared edge-case criteria — absence is meaningful information, not a zero.

## Conditional Evaluator Tools

Some evaluator tools are useful only on specific project types. Sprint 10 introduces `config.evaluator_tools` for declaring per-tool availability with backward-compatible defaults.

**`config.evaluator_tools.playwright`** — string. Default `"auto"`. Reserved values:

- `"auto"` — Playwright MCP is enabled when `config.project_type == "web-app"`, disabled otherwise. This is the recommended default.
- `"never"` — Playwright is unconditionally disabled. Use this when running a `web-app` project without Playwright installed; the Evaluator falls back to `curl` and routes Visual Design dimension findings to human review.
- `"always"` — Playwright is unconditionally enabled. Use only for explicit testing of the Playwright path in non-`web-app` projects.

**Why guard Playwright behind project type.** Playwright is the right tool for the Visual Design dimension of `web-app` evals (rendered DOM, computed styles, viewport extremes, JavaScript-driven UI). For other project types it adds tool surface without adding signal — `cli-tool`, `api-service`, `rag-system`, and `eval-harness` rubrics do not include a Visual Design dimension and do not need a browser harness.

**Visual Design fallback.** When `evaluator_tools.playwright` resolves to disabled on a `web-app` project, the Evaluator falls back to `curl` for HTTP-level verification and flags every Visual Design dimension finding as **low-confidence** in `## Human Review Flags`. Routing low-confidence Visual Design findings to human review is the documented escape hatch — silently grading without the right tool would produce confidently-wrong scores on a 25%-weight rubric dimension. See `agents/evaluator.md` under "Conditional Tools: Playwright MCP for Web Apps" for the full agent-facing instruction.

**Backward compatibility.** A project whose `.harness/config.json` lacks the `evaluator_tools` object hits the `"auto"` default. Combined with any non-`web-app` project type — including the current `eval-harness` project — `"auto"` resolves to "Playwright disabled," which is exactly Phase-1 behavior. No project that predates Sprint 10 sees a Playwright invocation. End-to-end Playwright invocation against a live `web-app` project is deferred to a synthetic verification sprint per the gap-closure plan, matching Sprint 8's posture for `thinking.profile` and Sprint 9's posture for transcript file writing.

## Sprint-State Phase-Qualifier Convention

`sprint-state.json` uses a namespaced key scheme to avoid collisions between
Phase 1 and Phase 2 sprint entries:

- **Phase 1** sprint entries use bare integer keys: `"1"` through `"12"`.
- **Phase 2** sprint entries use `phase-02-N` keys: `"phase-02-0"`, `"phase-02-1"`,
  `"phase-02-2"`, etc.
- The `current_phase` field disambiguates which phase `current_sprint` refers to:
  when `current_phase == 2`, `current_sprint: 2` means Phase 2 Sprint 2, whose
  state entry is keyed `"phase-02-2"`.
- **Bridging exception:** Sprint 0 of Phase 2 used the bare key `"0"` because
  Phase 1 had no Sprint 0 and no collision was possible. Sprint 1 introduced
  the `phase-02-N` form; Sprint 2+ use it exclusively.

Tooling that reads `sprint-state.json` must interpret `current_sprint` in the
context of `current_phase` — do not assume bare integer keys for Phase 2.

Sprint 0 introduced the `phase-02/` subdirectory for contract and eval files.

## Phase 2 Contract and Eval File Naming Convention

Phase 2 (Python library build, Sprints 00–06) contract files use a `phase-02/`
subdirectory under `.harness/contracts/`. Canonical paths for Phase 2 contract
artifacts:

- `.harness/contracts/phase-02/sprint-NN.md` — sprint contract markdown
- `.harness/contracts/phase-02/sprint-NN.tasks.json` — machine-readable tasks

## Phase 2 Eval File Naming Convention

Phase 2 (Python library build, Sprints 00–06) eval files use a `phase-02/`
subdirectory rather than the sprint-number-offset scheme proposed in `spec.md`.
The offset scheme (`NN + 5`) was written before Sprints 6–12 consumed those
numbers for Phase 2 meta-sprints; the `phase-02/` subdirectory avoids collisions
and makes the phase boundary unambiguous in `git log`.

Canonical path patterns for Phase 2 eval artifacts:

- `.harness/evals/phase-02/sprint-NN-rR.md` — single-trial eval (when `config.trials == 1`)
- `.harness/evals/phase-02/sprint-NN-rR-tT.md` — multi-trial eval (when `config.trials > 1`, `T` is 1-indexed trial number within round `R`)
- `.harness/transcripts/phase-02/sprint-NN-rR.json` — matching transcript (single-trial)
- `.harness/transcripts/phase-02/sprint-NN-rR-tT.json` — matching transcript (multi-trial)

Phase 1 eval files under `.harness/evals/sprint-0{1..5}-*.md` are unaffected
and remain at the root `evals/` path as append-only audit history. Phase 2
meta-sprint evals (sprint-06 through sprint-12) likewise remain at root path
as append-only history — only Sprints 00–06 of the Python library build use
the `phase-02/` subdirectory going forward.

## Adversarial Hygiene: `verified_via_command` Per Criterion

Sprint 9's transcript trailer captures messages, tool calls, token usage, timing, and thinking summary per evaluator run. Sprint 10 adds the per-criterion `verified_via_command` boolean to the same channel as the audit ground truth for "did the evaluator actually run the verification command, or did it grade by inference?"

**Per-criterion, not per-eval-file.** The flag is keyed by `task_id` so each criterion carries its own audit verdict — one verified criterion does not vouch for the others. A per-eval-file flag would be too coarse: it would let an evaluator run one `grep`, set the file-level flag to `true`, and grade the remaining nine criteria by inference without changing the flag. The per-criterion shape forces the evaluator to record, for each of N criteria, whether it actually executed the verification command versus inferring from non-executable evidence (filenames, comments, surrounding prose).

**Schema location.** The flag lives inside the Sprint 9 transcript trailer — see **Transcript Schema** above. Sprint 9 framed the trailer as "intentionally extensible"; Sprint 10 adds either a top-level `criteria_audit` array (`[{task_id, verified_via_command}, ...]`) or an inline `verified_via_command` field inside each `tool_calls` entry tagged with `task_id`. Both shapes preserve the per-criterion guarantee. The harness-summary skill consumes whichever shape is present and flags any criterion with `verified_via_command: false` as a candidate for human spot-check.

**No fabrication.** The Evaluator must not write `verified_via_command: true` for a criterion that was graded by reading prose, by inference from filenames, or by reasoning about code without running the verification command. Fabricated flags would hide exactly the criteria that need human review — defeating the calibration purpose of the audit channel. The no-fabrication rule matches Sprint 9's posture for `token_usage` and `timing`: better an honest `false` than a misleading `true`.

**No inference of PASS/FAIL from filenames or comments.** Beyond the per-criterion flag, the Evaluator's Adversarial Hygiene section in `agents/evaluator.md` forbids inferring verdicts from artifact metadata. A file named `success_FINAL.py` is not evidence of PASS; a `// TODO: broken` comment is not evidence of FAIL. The verdict for a deterministic criterion comes from the exit code of the verification command — nothing else. The verdict for an llm-judge criterion comes from structured rubric assessment of the artifact, not from signals embedded in its filename or comments.

**Backward compatibility.** A legacy evaluator that predates Sprint 10 does not emit `verified_via_command` flags; its trailer (if present) is missing the per-criterion audit channel. Sprint 9's failure-tolerant extraction stance applies — the harness-summary skill renders an "audit unavailable" note for those criteria rather than treating absence as failure. Projects that predate Sprint 9 entirely produce no trailer and no transcript file, so the question of `verified_via_command` does not arise.
