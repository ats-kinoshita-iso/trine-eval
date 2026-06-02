# Product Specification: trine-eval Self-Upgrade

## Product Vision

trine-eval is a three-agent eval-driven development harness. This specification
governs its evolution across two phases:

**Phase 1 — Self-Upgrade Against Eval-Driven Dev Playbook.** Upgrade trine-eval
to fully implement Anthropic's published eval-driven development methodology
(January–March 2026 guidance), closing 15 identified gaps against the playbook.
(Sprints 1–6, complete.)

**Phase 1.6 — Workflow-Step Port and Governance Hardening.** Close two
methodology gaps surfaced by the post-Sprint-9 council fan-out: (a) HK-0004 —
the in-repo `sprint-workflow/SKILL.md` is missing Steps 0.5, 1d, 3a-3e, 3d
that the Sprint-9 ported schema in `sprint-contract/SKILL.md` references; the
actual runtime loads cached v0.3.3 SKILL.md which has the steps, so it's a
documentation gap not an execution risk; and (b) HK-0003 — Sprints 7-9 ran
without the per-sprint council fan-out documented in `.council/config.json`
as `review_frequency: every-sprint`. Adds **bidirectional council-check gates**
to the workflow when governance is enabled (Architect P-05, extended
post-Sprint-10): a pre-sprint gate at Step 0 that warns when
`.council/sprint-prebrief/sprint-NN.json` is missing, and a post-sprint
auto-trigger at Step 5 completion that invokes `/henkaten-council:council-autorun`
for the sprint just completed before returning to the user. The auto-trigger
closes the HK-0003 manual-invocation gap by construction while respecting the
existing andon-stop protocol — an andon halt or autonomy-floor breach surfaces
to the user before further sprints are offered. Also adds a formal SN2
carve-out for renumbering-only edits to approved contracts (Scope Guardian
#5a + C-10), applied by fixing stale Sprint 9/10/11 references in
`sprint-07.md` / `sprint-08.md`. (Sprint 13, planned. Appended after Phase 2
completes so Phase 2 sprints 10-12 finish without further plan perturbation.)

**Phase 1.5 — Methodology Audit-Chain Repair.** Close a documented gap where
the `tasks.json` emission step described in `harness-sprint/SKILL.md` (Step 1d)
never produced output because its schema lived only in the published v0.3.3
plugin cache, not in the in-repo source `plugins/trine-eval/skills/sprint-contract/SKILL.md`.
Ports the schema from cache, adapts `grader_type` from the cached 2-way enum
to the repo's 3-way split (`behavioral` | `structural` | `llm-judge`, per
commit 408e8a2), back-fills `sprint-07.tasks.json` and `sprint-08.tasks.json`
from the existing approved markdown contracts. (Sprint 9, planned. Inserted
between Phase 1 and Phase 2 because audit-chain integrity is
methodology-foundational; sprints 1-6 back-fill is deferred follow-up.)

**Phase 2 — Agent-Harness Domain Support.** Extend trine-eval to drive
development of *agent runtime harnesses* (per "A Playbook for Building Agent
Harnesses"). Adds a new rubric, a Planner template tuned to the playbook's
dependency order, and a seed catalog of failure cases derived from the
playbook's documented traps. (Sprints 7-8 complete; sprints 10-12 planned —
renumbered from 9-11 when Sprint 9 [Phase 1.5] was inserted.)

The three phases share the harness's foundation (agents, skills, workflow) but
extend it along orthogonal axes: Phase 1 strengthens the eval methodology;
Phase 1.5 repairs the audit chain that connects contract → tasks.json →
regression gate → saturation graduation; Phase 2 broadens the project-type
coverage.

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

## Phase 1.5: Methodology Audit-Chain Repair

### Phase 1.5 Vision

The harness-sprint workflow defines a Step 1d `tasks.json` emission: after a
contract is APPROVED, the Generator transcribes the markdown contract into
`.harness/contracts/sprint-NN.tasks.json`. This JSON file is the
machine-readable source of record for three downstream consumers — the Step
0.5 regression gate, the Step 3d Batch API submission grouping, and the
harness-summary saturation-graduation step that promotes always-passing
criteria into a regression suite.

Sprints 5-8 of this self-upgrade project ran without `tasks.json` emission
because the schema the workflow references (`sprint-contract/SKILL.md` lines
90-132) is missing from the in-repo source — the schema lives only in the
published `v0.3.3` plugin cache. Phase 1.5 closes the divergence.

### Phase 1.5 Feature List

#### Phase 1.5 Must-have

A. **Tasks.json schema port** — Bring the `## Task Taxonomy: sprint-NN.tasks.json`
   section from cached `v0.3.3` `sprint-contract/SKILL.md` into the in-repo
   source. Additive port; the existing 87-line baseline is preserved.

B. **Grader-type 3-way adaptation** — The cached schema uses `grader_type:
   "deterministic" | "llm-judge"` (2-way). The repo adopted the 3-way split
   in commit `408e8a2`. The ported schema's `grader_type` enum is rewritten
   to `"behavioral" | "structural" | "llm-judge"` to match the methodology.

C. **Config taxonomy knob** — Add `config.taxonomy.emit_tasks_json: true`
   to `.harness/config.json`. Makes the gate the workflow expects explicit
   (today it implicitly defaults to true because the field is absent).

D. **Back-fill recent sprints** — Produce `.harness/contracts/sprint-07.tasks.json`
   (15 entries: 11 success + 4 Should-NOT) and `.harness/contracts/sprint-08.tasks.json`
   (19 entries: 13 success + 6 Should-NOT) by mechanical transcription from
   the approved markdown contracts. Sprints 1-6 back-fill is OUT of scope
   (deferred follow-up).

### Phase 1.5 Success Criteria

11. The in-repo `sprint-contract/SKILL.md` has a `## Task Taxonomy` section
    documenting the JSON shape, when to emit, and field semantics for all
    seven required fields (`task_id`, `criterion`, `grader_type`, `weight`,
    `is_gate`, `verification_command`, `rubric_dimension`).
12. The ported schema's `grader_type` enum is the 3-way set
    `{behavioral, structural, llm-judge}`, not the cached 2-way set.
13. `.harness/contracts/sprint-07.tasks.json` and `sprint-08.tasks.json`
    parse as valid JSON, contain the expected entry count (15 and 19), and
    each entry carries all required fields with `task_id` unique within its
    file.
14. `.harness/config.json` carries `taxonomy.emit_tasks_json: true`.
15. No prior sprint's markdown contract is modified by the back-fill.

### Phase 1.5 Explicit Non-Goals

- The `bucket` field (which the cached schema references via `rules/harness-conventions.md`)
  is OMITTED from the ported schema. A separate sprint can port the rules
  file and reintroduce `bucket` when needed.
- Back-fill for sprints 1-6 is NOT in scope. Those contracts predate the
  3-way grader split; back-filling them requires per-criterion classification
  decisions that Phase 1.5 deliberately defers.
- Arming the Step 0.5 regression gate (creating `.harness/regression/regression.json`)
  is NOT in scope. The gate activates when harness-summary first graduates a
  criterion via saturation analysis — separate trigger.
- Wiring `tasks.json` into Batch API submission is NOT in scope. Batch mode
  is not yet activated.
- Porting the cached Authoring Checklist, Subagent-Driven Behavioral
  Verification, or the trap-category enumeration is NOT in scope (separate
  methodology sprint).

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

**Phase 2 additional constraint:** No permanent example fixtures committed to the repo. Phase 2 Sprint 11 (renumbered from Sprint 10 after the Phase 1.5 insertion) validates the harness-build rubric against an ephemeral tmp-directory harness; findings persist as a single markdown report (`.harness/dogfood-findings.md`), not as committed source code.
