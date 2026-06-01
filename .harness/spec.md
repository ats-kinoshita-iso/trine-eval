# Product Specification: trine-eval Self-Upgrade

## Product Vision

trine-eval is a three-agent eval-driven development harness. This specification
governs its evolution across two phases:

**Phase 1 — Self-Upgrade Against Eval-Driven Dev Playbook.** Upgrade trine-eval
to fully implement Anthropic's published eval-driven development methodology
(January–March 2026 guidance), closing 15 identified gaps against the playbook.
(Sprints 1–6, complete.)

**Phase 2 — Agent-Harness Domain Support.** Extend trine-eval to drive
development of *agent runtime harnesses* (per "A Playbook for Building Agent
Harnesses"). Adds a new rubric, a Planner template tuned to the playbook's
dependency order, and a seed catalog of failure cases derived from the
playbook's documented traps. (Sprints 7–11, planned.)

The two phases share the harness's foundation (agents, skills, workflow) but
extend it along orthogonal axes: Phase 1 strengthens the eval methodology;
Phase 2 broadens the project-type coverage.

---

## Phase 1: Self-Upgrade Against Eval-Driven Dev Playbook

### Phase 1 Feature List

#### Must-have

1. **Grading hierarchy enforcement** — Evaluator distinguishes code-based graders (run first) from LLM-as-judge graders (for subjective dimensions). Contract criteria tagged by grader type.
2. **Negative test cases in contracts** — Contract template includes "Should NOT" criteria alongside "Should" criteria. Evaluator tests both.
3. **Reference solutions in contracts** — Contract template supports optional known-working outputs for calibration.
4. **Weighted criteria** — Each criterion in a sprint contract carries a weight. The evaluator computes a weighted score, not just pass/fail count.
5. **Environment isolation guidance** — Evaluator instructions specify clean-state requirements between trial runs.
6. **Pass@k and pass^k metrics** — eval-summary computes consistency metrics across retry rounds.
7. **Saturation graduation** — eval-summary identifies criteria that always pass and flags them for regression suite graduation.
8. **Plugin manifest accuracy** — plugin.json reflects the current project name and structure.
9. **JIT context retrieval patterns** — All agent and skill files document which context to read, at what step, and constrained to only what is necessary for that step.

#### Should-have

10. **Structured JSON state** — `sprint-state.json` alongside `progress.md` for machine-readable sprint state tracking.
11. **Per-dimension isolated judging** — Evaluator scores each rubric dimension in a separate reasoning pass, not all at once.
12. **Compaction guidance** — Generator and evaluator instructions include guidance for surviving context compaction in long sessions.
13. **Expanded hooks** — Hooks for pre-eval (ensure clean state), post-eval (update progress), and session-start (read progress).

#### Nice-to-have

14. **Human calibration pathway** — A mechanism for spot-checking evaluator grades against human judgment.
15. **ACI self-optimization** — Evaluator can review tool/skill descriptions and suggest improvements based on eval transcripts.
16. **Bootstrap from failures** — A workflow for importing real failure cases (bug reports, support tickets) as initial eval tasks.

### Phase 1 Success Criteria

1. The eval-harness rubric scores the upgraded system at 4+ on all five dimensions
2. All 8 playbook methodology steps have a corresponding mechanism in the harness
3. Contract template supports weighted criteria, negative tests, and reference solutions
4. Evaluator agent instructions enforce code→LLM→human grading hierarchy
5. eval-summary computes pass@k, pass^k, and saturation metrics
6. Plugin manifest and all cross-references are accurate
7. The eval-harness rubric scores Context Engineering at 5/5 — all five rubric requirements present: structured JSON state, prose/data format distinction, compaction guidance, sub-agent isolation with condensed summaries, and JIT context retrieval patterns documented

---

## Phase 2: Agent-Harness Domain Support

### Phase 2 Vision

trine-eval today drives the development of web apps, RAG systems, CLI tools,
APIs, and eval harnesses (itself). Phase 2 adds a sixth project type:
**agent runtime harnesses** — the engineering built around a model to make
it do useful work reliably (control plane, agentic loop, tool registry,
projection, skills, sandbox, observation, external affordances).

The reference source is "A Playbook for Building Agent Harnesses," a
dependency-ordered build procedure organized around nine stages plus a
cross-cutting governance principle. Phase 2 encodes the playbook into the
harness as: a domain rubric, a Planner template that mirrors the playbook's
dependency order, and a bootstrap failure catalog seeded from the playbook's
documented traps.

Phase 2 is additive — Phase 1 deliverables are not modified except via
Should-NOT-protected touchpoints declared in each Phase 2 sprint contract.

### Phase 2 Feature List

#### Phase 2 Must-have

17. **harness-build rubric** — 7-dimension rubric grading agent runtime harnesses against the playbook's stages, with hard thresholds for loop termination & bounds, sandboxing, and governance placement.
18. **Playbook traps catalog** — Bootstrap template seeding ~12–15 real failure cases from the playbook's "Trap" lines, organized under `templates/by-rubric/harness-build.json`.
19. **Harness-build Planner mode** — Project-type-aware sprint decomposition that mirrors the playbook's dependency order. Optional `playbook_stage` field on sprints.json entries, scoped to harness-build projects only.

### Phase 2 Success Criteria

8. A user running `/harness-kickoff` with a harness-build prompt receives a spec.md and sprints.json that align to the playbook's stage ordering
9. The harness-build rubric grades a deliberately minimal ephemeral harness fixture (no permanent `examples/` directory) with at least one trap-derived behavioral criterion exercising loop termination
10. Rubric decision guidance (in `eval-rubric` SKILL plus `rubrics/README.md`) routes users between `eval-harness` (meta — grades eval methodology) and `harness-build` (runtime — grades agent harness correctness) without manual specification

---

## User Interaction Patterns

Applies to both phases:

- Users invoke `/harness-kickoff` and `/harness-sprint` as before — no workflow changes
- New contract fields (weights, negative criteria, grader type) are additive — old contracts still work
- `eval-summary` gains new metric sections (pass@k, saturation) automatically
- Config gains optional fields with backward-compatible defaults

---

## Technical Constraints

Applies to both phases:

- All changes are to markdown, JSON, and YAML files — this is a Claude Code plugin, not runnable application code
- Agents communicate only via `.harness/` files
- Must remain compatible with Claude Code's plugin system (`plugin.json`, skills, agents, hooks)
- Skills must stay under 500 lines per SKILL.md
- No external dependencies — the harness runs purely through Claude Code's built-in tools

**Phase 2 additional constraint:** No permanent example fixtures committed to the repo. Phase 2 Sprint 10 validates the harness-build rubric against an ephemeral tmp-directory harness; findings persist as a single markdown report (`.harness/dogfood-findings.md`), not as committed source code.
