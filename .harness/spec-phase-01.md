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
