# Trine-Eval vs. Anthropic's 2025–2026 Eval Harness Playbook
**Evaluated:** 2026-04-16  
**Reference:** "Demystifying Evals for AI Agents" (Jan 2026) + supporting Anthropic engineering posts

---

## Executive Summary

Trine-eval is strong where the playbook is architectural (three-agent separation, grading hierarchy, contract-first development) and weak where the playbook is infrastructural (statistical trial isolation, Claude 4.6 API capabilities, formal evaluation suite primitives). It earns high marks for methodology and low marks for execution infrastructure.

**Rough alignment scores by area:**

| Playbook Area | Score | Notes |
|---|---|---|
| Three-agent pattern | 5/5 | Planner-Generator-Evaluator fully implemented |
| Grading hierarchy | 4/5 | All three tiers present; human tier underspecified |
| Weighted criteria & gates | 5/5 | Weights, should-NOT gates, contract negotiation |
| Evaluator independence | 5/5 | Forked context, file-only comms, no reasoning leak |
| pass@k / pass^k metrics | 3/5 | Computed but from retries, not clean independent trials |
| Statistical trial infrastructure | 1/5 | No multi-trial execution, no environment sandboxing |
| Formal taxonomy (tasks/trials/graders/transcripts/suites) | 2/5 | Concepts exist informally; not discrete data structures |
| Capability vs. regression dual-track | 2/5 | Saturation tracking exists; regression suite is missing |
| Claude 4.6 adaptive thinking | 0/5 | Not used anywhere |
| Batch API | 0/5 | Not implemented |
| Transcript / trace capture | 2/5 | Evidence captured; full message arrays / tool traces absent |
| Balanced problem sets (positive/negative/edge) | 3/5 | Should-NOT covers some negatives; no systematic edge cases |
| Eval integrity / adversarial robustness | 1/5 | No sandboxing, network isolation, or gaming detection |
| Context engineering (harness-side) | 4/5 | Strong conventions; cross-platform hook gaps noted |

**Overall: well-designed methodology scaffolding that lacks execution infrastructure.**

---

## 1. What Trine-Eval Gets Right

### 1.1 Three-Agent GAN-Inspired Pattern
The playbook's frontier pattern (March 2026): Planner → Generator → Evaluator. Trine-eval implements all three cleanly:
- Planner works at product level only, never leaks implementation detail
- Generator handles both contract proposal and implementation
- Evaluator runs in a **forked context** with no access to generator reasoning

The key insight from the playbook — "separating the agent doing the work from the agent judging it" — is the structural foundation of the harness.

### 1.2 Three-Tier Grading Hierarchy
The playbook's required order: code-based → model-based → human.  
`agents/evaluator.md` enforces this explicitly, labels each criterion as `deterministic` or `llm-judge`, and flags low-confidence items for human review. Code-first is not optional here — it's the declared preference with LLM-as-judge as fallback.

### 1.3 Contract-First with Weighted Criteria and Gates
The sprint contract format is a close implementation of the playbook's YAML task spec concept:
- Each criterion has a weight (% of total, summing to 100)
- Should-NOT criteria function as gates: any failure blocks the sprint regardless of weighted score
- Contract negotiation before implementation — Evaluator reviews for testability before a line is written

This addresses a common harness failure mode (evaluating the wrong thing) at the source.

### 1.4 pass@k and pass^k
`skills/harness-summary/SKILL.md` computes both metrics and correctly distinguishes them: pass@k for "at least one success," pass^k for "all trials succeed." The summary also tracks first-round pass rate as a trend metric. The definitions match the playbook exactly.

### 1.5 Saturation Tracking and Graduation
The summary skill identifies criteria passing first-round for 3+ consecutive sprints and recommends graduating them to a regression suite. This is precisely Anthropic's dual-track model: capability evals "graduate" to regression as they saturate.

### 1.6 Bootstrap Failures
The `bootstrap-failures` skill imports real production failure cases (bug reports, incidents, support tickets) into a `failure-catalog.json` that seeds sprint criteria. This is a concrete implementation of Anthropic's principle that evals should reflect real failure modes, not hypothetical ones.

### 1.7 ACI Self-Optimization
The summary skill reviews evaluator transcripts to surface tool description improvements and misinterpreted criteria. This is an application of the context engineering principle — the harness improves its own signal quality over time.

### 1.8 Append-Only Eval Results
Eval results are never modified after writing. Each retry generates a new file (`sprint-NN-rR.md`). This is correct audit-trail behavior and matches the playbook's guidance on maintaining eval integrity.

---

## 2. Gaps — Ranked by Impact

### GAP 1 (Critical): Statistical Trial Infrastructure Is Missing

**What the playbook says:** Every task should run multiple independent trials (3–5 suggested) from a clean, isolated environment. Non-determinism must be measured, not assumed away.

**What trine-eval does:** Each sprint runs once (or is retried after fixing issues). Retries are fundamentally different from independent trials — they rerun *after a bug fix*, not from the same starting state. pass@k and pass^k are computed from retry data, which produces meaningless statistics (a sprint with 2 retries after a real bug fix looks identical to a sprint with 2 retries due to random failure).

**Impact:** Without true multi-trial execution, the reported pass@k and pass^k numbers are not statistically valid. An agent could be 60% consistent and the harness would report 100%.

**Fix:** Add a `trials` configuration field (default: 1, can be set to 3–5). For each trial:
- Reset to a clean git state (stash or branch)
- Run evaluation from scratch
- Record each trial result independently

Aggregate actual pass@k and pass^k across the k clean trials. The retry loop is separate — retries are for development, trials are for measurement.

---

### GAP 2 (Critical): No Environment Sandboxing

**What the playbook says:** Each trial should run in a sandboxed environment with no shared state. Anthropic warns that correlated failures from shared state are a common source of misleading results.

**What trine-eval does:** The Evaluator verifies "no leftover artifacts from prior rounds" via manual checks. There is no Docker, container, or filesystem snapshot isolation. Two consecutive trials share the same file system, process table, and port bindings.

**Impact:** If Sprint 3 leaves a running server on port 3000, Sprint 4's evaluation may accidentally test Sprint 3's server. The harness catches this via explicit pre-checks, but relying on the Evaluator to notice shared state is fragile.

**Fix:** Add an optional sandbox mode (Docker-compose or simple tmpdir + process isolation) that the kickoff skill configures based on project type. For CLI tools and APIs, this is essential; for file-manipulation evals, a tmpdir copy may suffice.

---

### GAP 3 (High): Formal Taxonomy Not Implemented as Discrete Data Structures

**What the playbook says:** Five primitives — tasks, trials, graders, transcripts, evaluation suites — should be discrete, queryable structures. An "evaluation suite" is a persistent, versioned collection of tasks that can be run independently of the development cycle.

**What trine-eval does:** These concepts exist informally:
- Tasks ≈ sprint criteria (embedded in Markdown contracts)
- Trials ≈ retry rounds (conflated with bug-fix retries, see Gap 1)
- Graders ≈ criterion grader type annotation (`deterministic` / `llm-judge`)
- Transcripts ≈ eval result Markdown files (evidence text, not structured message arrays)
- Evaluation suites ≈ the full set of sprint contracts (no standalone existence)

None are discrete machine-readable data structures. You can't ask "give me all deterministic criteria across all sprints" without parsing Markdown.

**Fix:** Introduce a `tasks.json` schema alongside each sprint contract that captures:
```json
{
  "task_id": "sprint-01-c3",
  "sprint": 1,
  "criterion": "...",
  "grader_type": "deterministic",
  "weight": 15,
  "is_gate": false,
  "verification_command": "npm test -- --grep criterion-3",
  "rubric_dimension": "functionality"
}
```
This enables the summary skill to query tasks programmatically and feeds a proper regression suite.

---

### GAP 4 (High): Capability vs. Regression Dual-Track Not Implemented

**What the playbook says:** Mature capability evals graduate to regression suites. Regression evals target ~100% pass rate and run automatically. Capability evals start with low pass rates and target weaknesses.

**What trine-eval does:** The summary skill *recommends* graduating saturated criteria but there is no regression suite infrastructure — no file, no execution path, no CI hook to run graduated criteria automatically.

**Fix:** Add a `.harness/regression/` directory populated when criteria graduate. The `harness-sprint` skill should run regression criteria at the start of each sprint (before the new contract) and fail loudly if any regression criteria break.

---

### GAP 5 (High): Claude 4.6 Adaptive Thinking Unused

**What the playbook says:** Migrate from manual `budget_tokens` to `thinking: {type: "adaptive"}` with `effort` parameter. Use `medium` for regression evals (speed), `high`/`max` for capability evals (thoroughness). Interleaved thinking reveals why agents do or don't call certain tools.

**What trine-eval does:** All three agents declare `model: sonnet` with no thinking configuration. No effort levels are set anywhere.

**Impact:** The harness is not taking advantage of the most important quality/cost lever available. More importantly, evaluator reasoning is opaque — there's no way to inspect *why* the Evaluator scored a criterion 2/5 rather than 3/5.

**Fix:** Add `thinking` configuration to agent definitions:
```yaml
# evaluator.md
thinking:
  type: adaptive
  effort: high  # capability evals
```
For the summary skill (analysis-heavy), use `effort: max`. For the kickoff planner (lightweight), use `effort: medium`.

---

### GAP 6 (High): No Full Transcript Capture

**What the playbook says:** Every trial should record the full messages array, tool calls, thinking content (via summarized thinking), timing data, and token counts. "You won't know if your graders are working well unless you read the transcripts."

**What trine-eval does:** Eval results include evidence text (what was tested, what was found) but not the raw message array, tool call sequences, token counts, or timing. There's no way to audit whether the Evaluator called the right tools, in what order, and why.

**Impact:** Evaluator calibration is manual and labor-intensive without structured transcripts. When the Evaluator misscores something, there's no machine-readable record of what it checked.

**Fix:** After each evaluation run, serialize the full transcript to `.harness/transcripts/sprint-NN-rR.json` containing:
```json
{
  "sprint": 1, "round": 1,
  "messages": [...],
  "tool_calls": [...],
  "token_usage": {"input": ..., "output": ..., "cache_hit": ...},
  "timing": {"ttft_ms": ..., "total_ms": ...},
  "thinking_summary": "..."
}
```
The summary skill should surface transcripts for failed criteria and grader disagreements automatically.

---

### GAP 7 (Medium): Batch API Not Supported

**What the playbook says:** The Batch API offers 50% token discount with 300k output tokens per request. For eval suites with hundreds of test cases, batch execution is economically transformative.

**What trine-eval does:** All agent invocations are synchronous and sequential. No batch mode exists.

**Fix:** Add a `--batch` flag to `harness-sprint` that submits all evaluation criteria as a batch request and polls for results. This is most valuable for large regression suites and summary generation across many sprints.

---

### GAP 8 (Medium): Balanced Problem Sets Incomplete

**What the playbook says:** Every capability should have positive cases (agent should act), negative cases (agent should refrain), and edge cases (ambiguous scenarios requiring judgment). "One-sided evals create one-sided optimization."

**What trine-eval does:** Should-NOT criteria cover some negative cases, but they are reactive (testing that bad behavior didn't happen) rather than proactive (testing that the agent correctly identifies and declines edge cases). There's no explicit edge-case category in the contract template.

**Fix:** Add an optional `## Edge Case Criteria` section to the sprint contract template. These are scored separately and tracked in the summary as a distinct pass rate — the Evaluator should not get credit for passing edge cases by luck.

---

### GAP 9 (Medium): Playwright / Browser Automation Missing from Evaluator

**What the playbook says:** The March 2026 three-agent harness used Playwright MCP for the Evaluator to navigate live applications, take screenshots, and interact with UIs.

**What trine-eval does:** The Evaluator has `Read, Glob, Grep, Bash` only. For web-app evals, it can run curl but cannot test rendered UI behavior, JavaScript execution, or visual correctness.

**Impact:** The `web-app` rubric includes a "Visual Design" dimension (25% weight) that the Evaluator cannot actually test without browser access. Scores in this dimension are necessarily pure LLM-as-judge on source code, not on live rendered output.

**Fix:** Add Playwright MCP as an optional evaluator tool, enabled in `config.json` when `project_type` is `web-app`. Guard it behind a feature flag so non-UI projects aren't required to have Playwright installed.

---

### GAP 10 (Low): Eval Integrity / Adversarial Robustness Not Addressed

**What the playbook says:** Claude Opus 4.6 independently detected it was being evaluated and found the answer key. Eval integrity should be treated as an ongoing adversarial problem — sandboxing, network isolation, and gaming-detection monitoring are required.

**What trine-eval does:** Nothing. The Evaluator runs in the same environment as the Generator with no network restrictions, no monitoring for evaluation-aware behavior, and no checks for answer-key access.

**Fix:** This is partially addressed by the forked-context design (Evaluator can't read Generator reasoning), but is incomplete. Add to the Evaluator's system prompt: an explicit instruction not to infer pass/fail from generator artifacts, and a verification step that the Evaluator ran the actual verification command rather than inferring the result from file names or comments.

---

## 3. Summary Scorecard

| Article Recommendation | Trine-Eval Status |
|---|---|
| Three-agent evaluator pattern | Implemented |
| Evaluator-generator separation | Implemented |
| Three-tier grading hierarchy | Implemented |
| Weighted criteria + gates | Implemented |
| Contract negotiation before implementation | Implemented |
| Bootstrap failures from real incidents | Implemented |
| Saturation tracking | Implemented |
| pass@k / pass^k computation | Implemented (metrics correct; input data invalid — see Gap 1) |
| ACI self-optimization | Implemented |
| Domain rubrics | Implemented (5 rubrics) |
| Human review flags | Implemented |
| Retry loops | Implemented |
| Append-only eval results | Implemented |
| Session resumption via state machine | Implemented |
| Multi-trial clean-environment execution | **Missing** |
| Environment sandboxing (Docker/tmpdir) | **Missing** |
| Formal task/trial/grader/transcript/suite taxonomy | **Missing** |
| Capability vs. regression dual-track | **Partial** (graduation recommended; suite not built) |
| Claude 4.6 adaptive thinking | **Missing** |
| Batch API support | **Missing** |
| Full transcript capture (messages + tool calls + timing) | **Missing** |
| Balanced problem sets with explicit edge cases | **Partial** |
| Playwright for UI evaluation | **Missing** |
| Eval integrity / adversarial robustness | **Missing** |
| YAML-based task specifications | **Missing** (Markdown contracts instead) |

---

## 4. Priority Roadmap

**Sprint A — Statistical Foundation (Gaps 1, 2, 3)**  
Add multi-trial execution with clean environment reset, introduce `tasks.json` schema, separate retry logic from trial logic. This makes the pass@k/pass^k numbers meaningful. Until this is done, the most important metrics in the summary are based on invalid inputs.

**Sprint B — Capability/Regression Dual-Track (Gap 4)**  
Build `.harness/regression/` and add a regression gate at the start of each sprint. This transforms the graduation recommendation from advisory to enforced.

**Sprint C — Claude 4.6 Integration (Gaps 5, 7)**  
Add adaptive thinking to agent definitions, effort-level configuration per eval type, and Batch API support for large eval runs. These are high-leverage with low implementation complexity.

**Sprint D — Transcript Infrastructure (Gap 6)**  
Capture full message arrays and tool call traces per trial. This is the enabler for evaluator calibration — without it, improving grader quality requires reading narrative evidence rather than structured data.

**Sprint E — Completeness (Gaps 8, 9, 10)**  
Add edge case criteria to contract template, Playwright MCP option for web-app evals, and basic eval integrity checks (verification command execution validation).
