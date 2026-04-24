# Product Specification: trine-eval Self-Upgrade

## Product Vision

Upgrade trine-eval to fully implement Anthropic's published eval-driven development methodology (January–March 2026 guidance). The harness should move from a functional three-agent loop to a comprehensive eval framework that enforces the grading hierarchy, supports balanced test sets, tracks saturation, and manages context deliberately — closing 15 identified gaps against the playbook.

## Feature List

### Must-have

1. **Grading hierarchy enforcement** — Evaluator distinguishes code-based graders (run first) from LLM-as-judge graders (for subjective dimensions). Contract criteria tagged by grader type.
2. **Negative test cases in contracts** — Contract template includes "Should NOT" criteria alongside "Should" criteria. Evaluator tests both.
3. **Reference solutions in contracts** — Contract template supports optional known-working outputs for calibration.
4. **Weighted criteria** — Each criterion in a sprint contract carries a weight. The evaluator computes a weighted score, not just pass/fail count.
5. **Environment isolation guidance** — Evaluator instructions specify clean-state requirements between trial runs.
6. **Pass@k and pass^k metrics** — eval-summary computes consistency metrics across retry rounds.
7. **Saturation graduation** — eval-summary identifies criteria that always pass and flags them for regression suite graduation.
8. **Plugin manifest accuracy** — plugin.json reflects the current project name and structure.

### Should-have

9. **Structured JSON state** — `feature_list.json` alongside `progress.md` for machine-readable sprint state tracking.
10. **Per-dimension isolated judging** — Evaluator scores each rubric dimension in a separate reasoning pass, not all at once.
11. **Compaction guidance** — Generator and evaluator instructions include guidance for surviving context compaction in long sessions.
12. **Expanded hooks** — Hooks for pre-eval (ensure clean state), post-eval (update progress), and session-start (read progress).

### Nice-to-have

13. **Human calibration pathway** — A mechanism for spot-checking evaluator grades against human judgment.
14. **ACI self-optimization** — Evaluator can review tool/skill descriptions and suggest improvements based on eval transcripts.
15. **Bootstrap from failures** — A workflow for importing real failure cases (bug reports, support tickets) as initial eval tasks.

## User Interaction Patterns

- Users invoke `/harness-kickoff` and `/harness-sprint` as before — no workflow changes
- New contract fields (weights, negative criteria, grader type) are additive — old contracts still work
- `eval-summary` gains new metric sections (pass@k, saturation) automatically
- Config gains optional fields with backward-compatible defaults

## Technical Constraints

- All changes are to markdown, JSON, and YAML files — this is a Claude Code plugin, not runnable application code
- Agents communicate only via `.harness/` files
- Must remain compatible with Claude Code's plugin system (`plugin.json`, skills, agents, hooks)
- Skills must stay under 500 lines per SKILL.md
- No external dependencies — the harness runs purely through Claude Code's built-in tools

## Success Criteria

1. The eval-harness rubric scores the upgraded system at 4+ on all five dimensions
2. All 8 playbook methodology steps have a corresponding mechanism in the harness
3. Contract template supports weighted criteria, negative tests, and reference solutions
4. Evaluator agent instructions enforce code→LLM→human grading hierarchy
5. eval-summary computes pass@k, pass^k, and saturation metrics
6. Plugin manifest and all cross-references are accurate

## Phase 2: Playbook Alignment (Sprints 6–10)

Phase 1 (sprints 1–5) closed the methodology gaps in trine-eval against Anthropic's Jan–Mar 2026 eval playbook. The gap analysis at `.harness/playbook-alignment-2026-04.md` identified 10 remaining gaps in execution infrastructure — primarily statistical validity of pass@k/pass^k, Claude 4.6 API features, and formal evaluation suite primitives. The gap-closure plan at `.harness/gap-closure-plan-2026-04.md` maps these gaps to five new sprints.

### Must-have (Gaps 1–6)

16. **Multi-trial execution (Gap 1)** — Separate the retry loop (bug-fix) from the trial loop (measurement). When `config.trials > 1`, each trial runs from clean git state and writes its own eval file (`sprint-NN-rR-tT.md`). pass@k and pass^k are computed from trials, not rounds.
17. **Environment sandboxing (Gap 2)** — Add `config.sandbox.mode` with values `"none"`, `"tmpdir"`, and `"docker"`. Evaluator runs each trial in a fresh sandbox to eliminate cross-trial state contamination.
18. **Formal task taxonomy (Gap 3)** — Contract negotiation emits a sibling `sprint-NN.tasks.json` with one entry per criterion (`task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`) to serve as the machine-readable source of record for regression and batch scheduling.
19. **Regression gate (Gap 4)** — Saturated criteria graduate into `.harness/regression/regression.json`. Sprint workflow runs the regression suite before contract negotiation; any failure aborts the sprint.
20. **Adaptive thinking configuration (Gap 5)** — Agents declare `thinking: { type: adaptive, effort: ... }` frontmatter tuned to role: `medium` for planning and implementation, `high` for capability evals, `max` for contract review and summary analysis. Exposes a `thinking.profile` config knob.
21. **Full transcript capture (Gap 6)** — Evaluator emits a structured JSON trailer captured to `.harness/transcripts/sprint-NN-rR-tT.json` with messages, tool calls, token usage, timing, and thinking summary. Summary output links transcripts for any FAIL criterion or grader disagreement.

### Should-have (Gaps 7–10)

22. **Batch API mode (Gap 7)** — `config.batch.enabled` routes eval criterion verifications through Anthropic's Batch API when the criterion count meets `batch.min_criteria`. Documents the 50% discount and 24-hour SLA.
23. **Edge case criteria (Gap 8)** — Contract template supports an optional `## Edge Case Criteria` section. Edge-case pass rate is reported separately from weighted score.
24. **Playwright MCP evaluator (Gap 9)** — Evaluator conditionally enables Playwright when `config.project_type == "web-app"`; falls back to curl otherwise. Visual Design dimension findings are flagged low-confidence if Playwright is unavailable.
25. **Adversarial hygiene (Gap 10)** — Evaluator is instructed never to infer PASS/FAIL from filenames or comments, to log verification commands before scoring, and to emit a `verified_via_command` flag per criterion. Summary flags any criterion lacking verification evidence.

### Technical Constraints (Phase 2 additions)

- New `.harness/config.json` fields are optional with backward-compatible defaults: `trials: 1`, `sandbox.mode: "none"`, `thinking.profile: "default"`, `batch.enabled: false`, `batch.min_criteria: 20`, `transcripts.capture: true`, `transcripts.retain_days: 30`, `regression.enabled: true` (when `regression.json` exists), `regression.fail_fast: true`, `evaluator_tools.playwright: "auto"`, `taxonomy.emit_tasks_json: true`. An existing config file that predates Phase 2 must continue to execute exactly as it did before: one trial, no sandbox, synchronous calls, no transcript files, no regression gate.
- New directories introduced by Phase 2 (`.harness/regression/`, `.harness/transcripts/`, optional `scripts/`) are created on demand by the sprints that need them.
- Trial file naming extends round-file naming: `sprint-NN-rR-tT.md` (trials share a round, retries create a new round).

### Phase 2 Success Criteria

1. With `trials: 1` (default), Phase 2 harness behaves identically to Phase 1 — no behavior change for pre-existing projects
2. With `trials: k > 1`, eval-summary computes pass@k and pass^k from independent trial files, not retry rounds
3. Every graduated criterion lives in `regression.json` and blocks new sprints on regression failure
4. Agent frontmatter declares explicit adaptive-thinking effort levels tuned to agent role
5. Batch API mode cuts eval-time API calls from N to 1 on sprints with ≥ `batch.min_criteria` criteria
6. Evaluator transcripts are captured to `.harness/transcripts/` and linked from summary FAIL entries
7. Web-app projects invoke Playwright via MCP for Visual Design dimension criteria
8. No sprint eval grades a criterion PASS/FAIL without a recorded verification command
