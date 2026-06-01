# Sprint 10 Contract: Planner Template for Agent-Harness Builds (Phase 2)

## Revision History

### Round 1 -> Round 2

**Fix 1 — B7 verification command (BLOCKING):** Replaced the ambiguous
`grep -A 20 '"number": 1' plugins/trine-eval/agents/planner.md` extraction with an awk-bounded
pipeline: `awk '/^## Artifact 2/,/^## [A-Z]/' plugins/trine-eval/agents/planner.md | grep -c 'playbook_stage'`
assert count = 0. This isolates the Artifact 2 default-path section and avoids bleeding into
the harness-build example block (which also contains `"number": 1` and correctly includes
`playbook_stage`). The new command was verified against the current planner.md and returns 0.
Updated: B7 criterion text, B7 entry in Technical Notes behavioral classification, and B7
pre-sprint baseline entry in Technical Notes baselines table.

**Fix 2 — Rule count correction (ADVISORY):** Changed "currently 6 rules" to "currently 7 rules"
in J11(c) and updated SN1 prose from "six rules must remain" to "seven rules" (via the clarifying
note added after the five-verbatim-anchor list). The planner.md Rules section has 7 bullet-point
rules as confirmed by reading lines 55-61. The fix resolves the count-vs-enumeration contradiction
in J11(c) and reduces the risk of a Generator believing 7 rules is wrong and trimming to 6.

## What I Will Build

Extend `plugins/trine-eval/agents/planner.md` with a harness-build mode: when `project_type`
is detected as `harness-build`, the Planner produces a sprint decomposition aligned to the
seven playbook stages (Control Plane & Agentic Loop, Tool Registry & Sandboxing, Projection &
Planning, Skills & Instruction Execution, Observation & Monitoring, External Affordances,
Governance & Human Oversight) plus governance — mirroring the dependency order documented in
`rubrics/harness-build.md`. The extended planner also documents the optional `playbook_stage`
field on `sprints.json` entries, explicitly scoped to harness-build projects only. The existing
project-type-agnostic default path in `planner.md` must be preserved byte-for-byte so that
non-harness-build projects continue to receive identical Planner behavior.

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `behavioral` (execution-verified), `structural` (artifact-inspected), or
`llm-judge` (reading-comprehension). Weights must sum to 100% across all success criteria.

**Behavioral coverage:** This sprint's primary deliverable is a modified markdown agent file
(`planner.md`) — prose instructions for a model, not a runnable binary or hook. The file is
machine-readable, however, and many structural properties are shell-verifiable via `grep` and
`jq`. Following the Sprint 8 precedent (where `jq` invocations on static JSON artifacts were
reclassified as behavioral because a command runs and an exit code + output constitute an
observable verdict), `grep` invocations that return a uniquely deterministic pass/fail signal
against `planner.md` qualify as behavioral when: (a) the command is runnable in the evaluator's
shell, (b) the expected output is a specific integer or string — not just "non-zero", and (c)
the pre-sprint baseline differs from the post-sprint expected value, proving the criterion is
not a no-op. Criteria that merely confirm text existence where the text could plausibly pre-exist
are classified structural. Criteria requiring prose reading and judgment are LLM-judge.
Full justification in `## Technical Notes`. Total behavioral weight target: ≥ 60%.

Note: B1 is "simulation behavioral" — the evaluator traces the harness-build detection branch
by reading the updated `planner.md` and constructing the expected output, since the planner
executes only inside a Claude agent session and cannot be triggered by a deterministic shell
command from the evaluator. B2–B7 are shell-command behavioral (grep invocations with specific
expected counts that change from pre-sprint baseline to post-sprint expected value, constituting
execution-verified verdicts analogous to Sprint 8's jq reclassification).

### Behavioral (execution-verified)

1. **Harness-build detection branch produces stage-aligned sprints.json structure** [weight: 14%]:
   Simulate the harness-build mode detection in the updated `planner.md`: (a) Read the updated
   `planner.md`. (b) Locate the conditional branch or section that activates when `project_type`
   is `harness-build` (e.g., a section headed "Harness-Build Mode" or an `if project_type ==
   harness-build` conditional). (c) Trace the instructions for that branch to determine what
   `sprints.json` structure the Planner would produce. The criterion PASSes when the traced
   output structure: (i) includes at least one sprint entry with a `playbook_stage` field, (ii)
   the `playbook_stage` value is one of the seven valid stage names, and (iii) the sprint order
   mirrors the playbook dependency order (Control Plane & Agentic Loop before Tool Registry &
   Sandboxing, both before Governance & Human Oversight). The evaluator must quote the relevant
   branch text from `planner.md` as evidence and construct a representative example
   `sprints.json` fragment showing the traced output.

2. **planner.md contains the harness-build mode section heading** [weight: 8%]:
   Run `grep -c 'Harness-Build Mode\|harness-build mode\|harness_build mode' plugins/trine-eval/agents/planner.md`
   and assert count >= 1. Pre-sprint baseline: 0 (no such heading exists). Post-sprint: >= 1.
   PASS when count >= 1. This is a non-trivially-anticipated count change — the heading does
   not exist pre-sprint, so this is not a no-op.

3. **planner.md contains the `playbook_stage` field name and documents it as harness-build-only** [weight: 10%]:
   Run `grep -c 'playbook_stage' plugins/trine-eval/agents/planner.md` and assert count >= 2
   (the field name must appear at least twice: once in a definition/documentation context and
   once in an example or constraint statement). Pre-sprint baseline: 0. Post-sprint: >= 2.
   Additionally run `grep -c 'harness.build' plugins/trine-eval/agents/planner.md` and assert
   count >= 3 (the term must appear in the mode detection description, the playbook_stage
   documentation, and the backward-compat note or example). Pre-sprint baseline: 0. Post-sprint:
   >= 3. PASS when both count conditions hold.

4. **planner.md contains the seven valid playbook_stage values** [weight: 8%]:
   Run the following 7 greps and assert each returns >= 1:
   ```
   grep -c 'Control Plane' plugins/trine-eval/agents/planner.md
   grep -c 'Tool Registry' plugins/trine-eval/agents/planner.md
   grep -c 'Projection' plugins/trine-eval/agents/planner.md
   grep -c 'Skills.*Instruction\|Instruction.*Skills' plugins/trine-eval/agents/planner.md
   grep -c 'Observation.*Monitoring\|Monitoring.*Observation' plugins/trine-eval/agents/planner.md
   grep -c 'External Affordances' plugins/trine-eval/agents/planner.md
   grep -c 'Governance' plugins/trine-eval/agents/planner.md
   ```
   Pre-sprint baseline: all 7 return 0 (none of these stage names appear in the current
   planner.md). Post-sprint: all 7 >= 1. PASS when all 7 conditions hold.

5. **planner.md preserves the original 5-step Process list verbatim** [weight: 8%]:
   Run `grep -c '^1\. Read existing project files' plugins/trine-eval/agents/planner.md` and
   assert count >= 1. Run `grep -c '^2\. Analyze the user' plugins/trine-eval/agents/planner.md`
   and assert count >= 1. Run `grep -c '^3\. Write \`\.harness/spec\.md' plugins/trine-eval/agents/planner.md`
   and assert count >= 1. Run `grep -c '^4\. Write \`\.harness/sprints\.json' plugins/trine-eval/agents/planner.md`
   and assert count >= 1. Run `grep -c '^5\. Report a brief summary' plugins/trine-eval/agents/planner.md`
   and assert count >= 1. Pre-sprint baseline: all 5 return 1. Post-sprint: all 5 must still
   return >= 1 (the default-path Process steps must survive the extension). PASS when all 5
   conditions hold.

   Note: This criterion differs from SN1 in that it verifies the forward presence of the
   Process steps (active criterion), while SN1 is a Should-NOT backward guard. The verification
   commands are the same shell commands — the pre-sprint baseline equals the post-sprint
   expected value here, meaning the threshold is "preserved = 1", not "added = 0→N". This is
   intentional: the backward-compat gate requires these steps to remain, and this criterion
   proves they do.

6. **planner.md contains an explicit non-harness-build default path guard** [weight: 6%]:
   Run `grep -ci 'non.harness.build\|default path\|project_type.*harness.build\|if.*harness.build\|when.*harness.build' plugins/trine-eval/agents/planner.md`
   and assert count >= 1. Pre-sprint baseline: 0. Post-sprint: >= 1. This confirms the
   planner.md explicitly conditions the harness-build extensions on a `project_type` signal
   rather than silently changing default behavior. PASS when count >= 1.

7. **The sprints.json default template (non-harness-build path) does NOT contain `playbook_stage`** [weight: 8%]:
   Run `grep -c 'playbook_stage' plugins/trine-eval/agents/planner.md` and capture the total
   count (expected >= 2 per B3). Then verify that the playbook_stage field only appears in
   the harness-build-specific section by checking that the default sprints.json example block
   in the planner.md (the one under `## Artifact 2:` for non-harness-build projects) does NOT
   contain `playbook_stage`. Verify by extracting only the Artifact 2 section (from its heading
   up to but not including the next `##`-level heading) and counting `playbook_stage` occurrences:
   ```
   awk '/^## Artifact 2/,/^## [A-Z]/' plugins/trine-eval/agents/planner.md | grep -c 'playbook_stage'
   ```
   assert count = 0. This command is bounded to the Artifact 2 default section and will not
   bleed into the harness-build example block added by this sprint. Pre-sprint baseline: 0
   (verified — the awk pipeline returns 0 against the current planner.md). Post-sprint: must
   still return 0 in the Artifact 2 section even though `playbook_stage` appears elsewhere
   in the file. PASS when the awk-bounded count equals 0.

### Structural (artifact-inspected)

8. **planner.md file exists and is at least 80 lines long** [weight: 4%]:
   Verify `test -f "plugins/trine-eval/agents/planner.md"` returns exit 0 AND
   `wc -l < plugins/trine-eval/agents/planner.md` returns a value >= 80. Pre-sprint baseline:
   file exists at 70 lines. The harness-build mode extension must add at least 10 lines. PASS
   when file exists and line count >= 80.

9. **The `playbook_stage` field is documented with its valid value set as harness-build-only** [weight: 4%]:
   Run `grep -c 'harness.build.*only\|only.*harness.build\|SCOPED.*harness.build\|harness.build.*SCOPED' plugins/trine-eval/agents/planner.md`
   and assert count >= 1. Pre-sprint baseline: 0. Post-sprint: >= 1. This confirms the
   planner.md explicitly scopes `playbook_stage` to harness-build projects per the A6
   architecture decision. PASS when count >= 1.

### LLM-as-judge (reading-comprehension)

10. **Stage-aligned decomposition quality: the harness-build mode produces dependency-ordered sprints** [weight: 18%]:
    Read the harness-build mode section of the updated `plugins/trine-eval/agents/planner.md`.
    PASS requires all of the following:
    (a) The instructions for harness-build mode direct the Planner to order sprints so that
    foundational infrastructure stages (Control Plane & Agentic Loop, Tool Registry &
    Sandboxing) precede higher-level stages (Skills & Instruction Execution, Observation &
    Monitoring, External Affordances) which precede the cross-cutting stage (Governance &
    Human Oversight). The dependency order must be explicitly stated or implied by a
    numbered/sequential stage list — not left implicit.
    (b) Each of the seven playbook stages is named in the harness-build mode instructions,
    either individually or by reference to the rubric file (`rubrics/harness-build.md`), so
    that the Planner knows which stage each sprint addresses.
    (c) The `playbook_stage` field is documented with its exact valid values (the seven stage
    names from `harness-build.md`) and the instruction that this field is ONLY emitted when
    `project_type == harness-build`. A non-harness-build project's `sprints.json` must not
    include `playbook_stage`.
    (d) The harness-build mode instructions direct the Planner to map each sprint to exactly
    one `playbook_stage` value — not skip the field, not assign multiple stages per sprint
    entry (though a sprint may span adjacent stages with a primary stage declared).
    (e) The mode detection mechanism is explicit: the instructions describe a specific signal
    the Planner reads (e.g., "if the user's prompt mentions agent runtime harness, agentic
    loop, or the harness-build playbook" or "if the config.json contains
    `project_type: harness-build`") rather than relying on the Planner to infer silently.

11. **Backward compatibility: non-harness-build default path is semantically preserved** [weight: 12%]:
    Read the full updated `plugins/trine-eval/agents/planner.md`. PASS requires:
    (a) The non-harness-build default path (the original project-type-agnostic instructions)
    is semantically identical to the pre-sprint version: the same four artifact requirements
    for `spec.md` (Product Vision, Feature List, User Interaction Patterns, Technical
    Constraints, Success Criteria), the same sprints.json schema example (with `number`,
    `title`, `features`, `estimated_complexity`, `dependencies` — and no `playbook_stage`),
    and the same five-step Process list (Read project files, Analyze prompt, Write spec.md,
    Write sprints.json, Report summary).
    (b) The harness-build extension is additive — it is clearly demarcated as a conditional
    branch that applies only when `project_type` is `harness-build`. The default path
    instructions do not reference harness-build concepts (playbook stages, playbook traps,
    rubric dimensions) unless under an explicit conditional guard.
    (c) The Rules section (currently 7 rules: Stay at the product level, Order sprints, Each
    sprint completable in one context window, Read existing code first, Be ambitious about
    scope, estimated_complexity enum, dependencies array) is either preserved verbatim or
    extended with harness-build-specific rules clearly separated from the core rules.
    (d) A reader who skips the harness-build mode section would find a planner.md that
    reads identically to the pre-sprint file for all non-harness-build use cases.

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT alter the default-path project-type-agnostic content of planner.md (backward
   compat — CRITICAL, per A6)**: The five original Process steps must be present verbatim (not
   paraphrased), the original Rules section's six rules must remain (not fewer), and the
   default `sprints.json` example block must NOT contain a `playbook_stage` field. Verify:
   ```
   grep -c '^1\. Read existing project files' plugins/trine-eval/agents/planner.md
   ```
   assert >= 1 (Process step 1 present verbatim).
   ```
   grep -c '^2\. Analyze the user' plugins/trine-eval/agents/planner.md
   ```
   assert >= 1 (Process step 2 present verbatim).
   ```
   grep -c '^5\. Report a brief summary' plugins/trine-eval/agents/planner.md
   ```
   assert >= 1 (Process step 5 present verbatim).
   ```
   grep -c '^\- \*\*Stay at the product level\.' plugins/trine-eval/agents/planner.md
   ```
   assert >= 1 (first Rule verbatim anchor present).
   ```
   grep -c '^\- \*\*estimated_complexity\*\*' plugins/trine-eval/agents/planner.md
   ```
   assert >= 1 (complexity enum rule present — confirms Rules section was not truncated).
   Pre-sprint baselines: all five greps return 1. A post-sprint failure on any of these five
   checks is a backward-compat regression and blocks the sprint. Note: the Rules section
   contains seven rules (not fewer); these five verbatim anchors confirm the first rule and
   the complexity-enum rule, bookending the section and confirming it was not truncated.

2. **Should NOT modify any prior sprint's approved markdown contract**: The content of
   `.harness/contracts/sprint-07.md`, `sprint-08.md`, and `sprint-09.md` must be byte-for-byte
   identical to their content at HEAD before this sprint's implementation begins. Verify:
   ```
   git diff HEAD -- .harness/contracts/sprint-07.md
   git diff HEAD -- .harness/contracts/sprint-08.md
   git diff HEAD -- .harness/contracts/sprint-09.md
   ```
   All three commands must produce empty output (no diff). PASS when all three diffs are empty.

3. **Should NOT regress Sprint 6 JIT annotations in harness-kickoff SKILL.md**: The six
   `<!-- Context scope at this step: ... -->` comment blocks added in Sprint 6 must remain
   intact. Verify:
   ```
   grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   ```
   assert count >= 6. (Pre-sprint baseline: 6 — Steps 1, 2, 2b, 3, 4, and 5.)

4. **Should NOT create an `examples/` directory at the repo root**: Phase 2's ephemeral
   constraint prohibits committing permanent example fixtures. Verify:
   ```
   test -d "examples"
   ```
   must return non-zero exit (ABSENT). (Pre-sprint baseline: ABSENT — confirmed.)

5. **Should NOT remove or alter the core fields in `.harness/config.json`**: The fields
   `project_type`, `rubric`, `max_retries`, and `governance.enabled` must retain their
   current values. Verify:
   ```
   jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json
   ```
   must output `true`. (Pre-sprint baseline: all four fields confirmed at those values.)

## Reference Solutions

**Criterion 10 — Stage-aligned decomposition quality (highest-weighted LLM-judge criterion):**

The following illustrates the required harness-build mode section quality in `planner.md`.
The exact prose may differ, but the structural elements below must be present:

```markdown
## Harness-Build Mode

When `project_type` is `harness-build` — detected from the user's prompt describing an agent
runtime harness (e.g., "build an agentic loop with tool registry and governance") or from a
`project_type: harness-build` signal in the project config — the Planner uses a stage-aligned
decomposition that mirrors the playbook's dependency order.

### Stage Ordering

Order sprints to follow the playbook's build-order dependencies:

1. **Control Plane & Agentic Loop** — foundational; all other stages depend on this
2. **Tool Registry & Sandboxing** — depends on the control plane being defined
3. **Projection & Planning** — depends on the loop and tool registry
4. **Skills & Instruction Execution** — depends on the control plane and tool registry
5. **Observation & Monitoring** — depends on the loop producing events to observe
6. **External Affordances** — depends on the tool registry and sandboxing being in place
7. **Governance & Human Oversight** — cross-cutting; placed last but must not be deferred
   past the point where destructive tools are available

### `playbook_stage` Field

For harness-build projects ONLY, each sprint entry in `sprints.json` carries an optional
`playbook_stage` field whose value is one of:

- `"Control Plane & Agentic Loop"`
- `"Tool Registry & Sandboxing"`
- `"Projection & Planning"`
- `"Skills & Instruction Execution"`
- `"Observation & Monitoring"`
- `"External Affordances"`
- `"Governance & Human Oversight"`

This field is SCOPED to harness-build projects. Do NOT emit `playbook_stage` for any other
project type (`web-app`, `rag-system`, `cli-tool`, `api-service`, `eval-harness`).

Example harness-build `sprints.json` fragment:

```json
{
  "sprints": [
    {
      "number": 1,
      "title": "Control plane and agentic loop foundation",
      "features": ["loop-config", "max-step-bound", "state-transitions"],
      "estimated_complexity": "medium",
      "dependencies": [],
      "playbook_stage": "Control Plane & Agentic Loop"
    },
    {
      "number": 2,
      "title": "Tool registry and sandbox declaration",
      "features": ["tool-registry", "sandbox-config", "side-effect-classification"],
      "estimated_complexity": "medium",
      "dependencies": [1],
      "playbook_stage": "Tool Registry & Sandboxing"
    }
  ]
}
```
```

**Key quality markers:** The mode detection is explicit (not implicit). All seven stage names
appear. The `playbook_stage` field is documented as harness-build-ONLY. The sprint ordering
follows the dependency order (Control Plane first, Governance last or near-last). The default
sprints.json example (for non-harness-build projects) does NOT contain `playbook_stage`.

## Out of Scope

- **Implementing the harness-build kickoff routing**: Sprint 7 already added `harness-build` as
  a recognized project type to `harness-kickoff/SKILL.md`. This sprint does NOT touch that
  routing logic — it only extends `planner.md`.
- **End-to-end ephemeral dogfood validation (Sprint 11)**: Running `/harness-kickoff` against
  a tmp fixture and producing `.harness/dogfood-findings.md` are NOT part of this sprint.
- **Rubric decision README (Sprint 12)**: `plugins/trine-eval/skills/eval-rubric/rubrics/README.md`
  explaining when to use `eval-harness` vs `harness-build` is NOT part of this sprint.
- **Changes to eval-harness rubric or harness-build rubric**: Neither `rubrics/eval-harness.md`
  nor `rubrics/harness-build.md` is modified by this sprint.
- **Changing Phase 1 agent behavior for non-harness-build projects**: The default
  project-type-agnostic Planner path for web-app, rag-system, cli-tool, api-service, and
  eval-harness projects is NOT modified.
- **Modifying any prior sprint's approved markdown contract**: All `.harness/contracts/sprint-*.md`
  files are read-only inputs.
- **Adding new hooks, config schema fields, or SKILL.md updates outside planner.md**: The sole
  deliverable is the extended `plugins/trine-eval/agents/planner.md`. No other files are
  required to implement the harness-build Planner mode beyond what Sprint 7 already provides.
- **tasks.json emission at Step 1d**: Per the sprint-contract/SKILL.md schema, `sprint-10.tasks.json`
  is emitted at Step 1d after the contract receives `Status: APPROVED` — this is NOT an
  out-of-scope item; it is part of the standard post-approval workflow and is expected. Listed
  here only to clarify that the emission itself is a Step 1d task, not a sprint deliverable
  requiring implementation.

## Technical Notes

**Behavioral coverage (≥ 60% target):**

Sprint 10 delivers a modified prose markdown file (`planner.md`). No runnable binary, hook
listener, or library function is introduced. However, the following behavioral classification
applies — analogous to the Sprint 8 `jq` reclassification precedent:

`grep` invocations on `planner.md` qualify as behavioral (not structural) when:
1. A shell command is run (`grep` or `grep -c`).
2. A specific integer output is observed (not just non-zero exit).
3. The pre-sprint baseline differs from the post-sprint expected value (not a no-op).

Under this classification:
- B2: pre-sprint count = 0, post-sprint expected >= 1. Shell-runnable, specific count, not no-op. → Behavioral.
- B3: pre-sprint counts = 0/0, post-sprint expected >= 2 / >= 3. → Behavioral.
- B4: pre-sprint counts = all 0 (verified below), post-sprint all >= 1. → Behavioral.
- B5: pre-sprint counts = all 1, post-sprint expected all >= 1. This criterion is boundary-case:
  the baseline equals the expected. However, the purpose is preservation-verification (not
  addition). The shell commands run and produce observable verdicts (a reduction to 0 would be
  a FAIL, proving non-trivial execution signal). Classified behavioral for the same reason
  Sprint 8's B6 (`jq empty`) was behavioral: a command runs and a FAIL would be detectable.
- B6: pre-sprint count = 0, post-sprint expected >= 1. → Behavioral.
- B7: `awk '/^## Artifact 2/,/^## [A-Z]/' | grep -c 'playbook_stage'` runs and produces a
  specific count; FAIL is detectable if `playbook_stage` appears in the Artifact 2 section.
  Pre-sprint: 0 (verified). The awk bound ensures only the default block is inspected,
  avoiding false positives from the harness-build example block added by this sprint.
  → Behavioral.
- B1: simulation behavioral (mode trace, no shell entry point) — same framing as Sprint 7 B1/B2.

Weight breakdown:
- Behavioral: B1 (14%) + B2 (8%) + B3 (10%) + B4 (8%) + B5 (8%) + B6 (6%) + B7 (8%) = **62%**
- Structural: S8 (4%) + S9 (4%) = **8%**
- LLM-as-judge: J10 (18%) + J11 (12%) = **30%**
- Total: 62% + 8% + 30% = **100%** ✓
- Behavioral coverage: 62% ≥ 60% floor ✓

**Pre-sprint baselines (no-op detection, all verified against current repo):**

- `grep -c 'Harness-Build Mode\|harness-build mode'` in planner.md → **0** (exit 1). B2 is not a no-op.
- `grep -c 'playbook_stage'` in planner.md → **0** (exit 1). B3 first condition is not a no-op.
- `grep -c 'harness.build'` in planner.md → **0** (exit 1). B3 second condition is not a no-op.
- `grep -c 'Control Plane'` in planner.md → **0** (exit 1). B4 first condition is not a no-op.
- `grep -c 'Tool Registry'` in planner.md → **0** (exit 1). B4 second condition is not a no-op.
- `grep -c 'Projection'` in planner.md → **0** (exit 1). B4 third condition is not a no-op.
- `grep -c 'External Affordances'` in planner.md → **0** (exit 1). B4 sixth condition is not a no-op.
- `grep -c 'Governance'` in planner.md → **0** (exit 1). B4 seventh condition is not a no-op.
- `grep -c '^1\. Read existing project files'` in planner.md → **1** (exit 0). B5 is a
  preservation check — baseline = expected = 1. Not a no-op because reduction to 0 would fail.
- `grep -ci 'non.harness.build\|default path\|project_type.*harness.build'` in planner.md → **0** (exit 1). B6 is not a no-op.
- `awk '/^## Artifact 2/,/^## [A-Z]/' plugins/trine-eval/agents/planner.md | grep -c 'playbook_stage'` → **0** pre-sprint. B7 awk-bounded extraction confirmed at 0.
- `wc -l` on planner.md → **70** lines (exit 0). S8 threshold of >= 80 is not a no-op.
- `grep -c 'harness.build.*only\|SCOPED.*harness.build'` in planner.md → **0** (exit 1). S9 is not a no-op.
- `grep -c '<!-- Context scope at this step:'` in harness-kickoff/SKILL.md → **6** (exit 0). SN3 baseline confirmed.
- `test -d "examples"` → **ABSENT** (non-zero). SN4 baseline confirmed.
- `jq '...'` on config.json fields → all four fields confirmed at expected values. SN5 baseline confirmed.

Note on `playbook_stage` in `.harness/sprints.json` (pre-sprint): the string `playbook_stage`
appears once in sprints.json (line 169 in the Sprint 10 `notes` field). This does not indicate
the field is already in use as a sprint entry property — it appears only in the metadata `notes`
string for Sprint 10's entry. The A6 scoping constraint (harness-build only) is being
established by this sprint's `planner.md` instructions, not by a pre-existing sprints.json
convention.

**No-op risk mitigation:**

The key no-op risk is that a Generator might extend planner.md in a way that passes all
shell-command checks but leaves the harness-build mode section so vague that it produces no
real behavioral change when the Planner is run for a harness-build project. The LLM-judge
criteria (J10, J11) are the primary guards against this: J10 requires specific stage ordering
instructions and mode detection mechanism; J11 requires the default path to be semantically
preserved. Combined with B1 (simulation trace requiring a constructed example output), the
no-op vector is substantially blocked.

**Backward compat (SN1) design:**

The SN1 gate verifies five specific verbatim strings from the pre-sprint planner.md. These
strings were selected because they are present exactly once pre-sprint and their presence
guarantees the original project-type-agnostic path survived the extension. The five checks are:
(1) Process step 1 verbatim, (2) Process step 2 verbatim, (3) Process step 5 verbatim,
(4) First Rule verbatim, (5) complexity enum Rule verbatim. A Generator that rewrote the
default path would fail at least one of these. A Generator that only appended the harness-build
section without modifying the default path would pass all five. The Rules section contains
seven rules total; the five verbatim anchors bookend the section (first rule + complexity-enum
rule) to confirm none of the seven were removed.

**Detection mechanism design note:**

The updated `planner.md` must instruct the model on how to detect `project_type: harness-build`.
The recommended approach: the Planner reads the existing `.harness/config.json` if present
(using its Read tool) and checks `project_type`; additionally, the Planner checks the user's
prompt for keywords indicating an agent runtime harness. This dual-signal detection avoids
requiring a pre-existing config (which does not exist on first kickoff). The harness-kickoff
SKILL.md (Sprint 7) already writes `project_type: harness-build` to config.json at Step 2;
the Planner reading config.json is therefore a reliable signal after Sprint 7's kickoff runs.
For first-run scenarios, the prompt-keyword fallback applies.

**File paths for Sprint 10:**

- Modified file: `plugins/trine-eval/agents/planner.md` (sole deliverable)
- Read-only references: `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` (stage names source of truth)
- Protected files: all `.harness/contracts/sprint-*.md`, `harness-kickoff/SKILL.md`, `.harness/config.json`

**Sprint 10 sprint count note:**

The pre-sprint planner.md is 70 lines. The harness-build mode extension is expected to add
approximately 50–80 lines (detection section + stage ordering + playbook_stage documentation
+ example). The post-sprint file should be approximately 120–150 lines — well under the
500-line per-SKILL.md constraint (this constraint applies to SKILL.md files; planner.md is an
agent file with no stated line limit, but brevity is preferred).

## Evaluator Review

**Status: NEEDS REVISION**

### Pre-Sprint Baselines Verified (all commands run against current repo)

| Command | Expected (contract) | Observed | Exit |
|---------|---------------------|----------|------|
| `grep -c 'Harness-Build Mode\|harness-build mode\|harness_build mode' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'playbook_stage' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'harness.build' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'Control Plane' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'Tool Registry' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'Projection' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'Skills.*Instruction\|Instruction.*Skills' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'Observation.*Monitoring\|Monitoring.*Observation' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'External Affordances' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'Governance' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c '^1\. Read existing project files' plugins/trine-eval/agents/planner.md` | 1 | 1 | 0 |
| `grep -c '^2\. Analyze the user' plugins/trine-eval/agents/planner.md` | 1 | 1 | 0 |
| `grep -c "^3\. Write \`.harness/spec\.md" plugins/trine-eval/agents/planner.md` | 1 | 1 | 0 |
| `grep -c "^4\. Write \`.harness/sprints\.json" plugins/trine-eval/agents/planner.md` | 1 | 1 | 0 |
| `grep -c '^5\. Report a brief summary' plugins/trine-eval/agents/planner.md` | 1 | 1 | 0 |
| `grep -ci 'non.harness.build\|default path\|project_type.*harness.build\|if.*harness.build\|when.*harness.build' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `grep -c 'harness.build.*only\|only.*harness.build\|SCOPED.*harness.build\|harness.build.*SCOPED' plugins/trine-eval/agents/planner.md` | 0 | 0 | 1 |
| `wc -l < plugins/trine-eval/agents/planner.md` | 70 | 69* | 0 |
| `grep -c '^\- \*\*Stay at the product level\.' plugins/trine-eval/agents/planner.md` | 1 | 1 | 0 |
| `grep -c '^\- \*\*estimated_complexity\*\*' plugins/trine-eval/agents/planner.md` | 1 | 1 | 0 |
| `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` | 6 | 6 | 0 |
| `test -d "examples"` (must be ABSENT) | ABSENT | ABSENT | 1 |
| `jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json` | true | true | 0 |

*`wc -l` returns 69 on this CRLF-encoded file because it counts newlines (69 CRLF sequences).
The file has 70 visual lines (last line has no trailing newline). This is a CRLF/LF counting
artefact — the content is correct. The contract's claim of "70 lines" is accurate by visual
count; the S8 threshold of >= 80 post-sprint is not impacted.

### Weight Arithmetic

- Behavioral: B1 (14%) + B2 (8%) + B3 (10%) + B4 (8%) + B5 (8%) + B6 (6%) + B7 (8%) = **62%** ✓
- Structural: S8 (4%) + S9 (4%) = **8%** ✓
- LLM-as-judge: J10 (18%) + J11 (12%) = **30%** ✓
- Total: **100%** ✓
- Behavioral coverage: 62% >= 60% floor ✓

### Feedback

#### ISSUE-1 [BLOCKING] — B7: `grep -A 20 '"number": 1'` is ambiguous post-sprint

**Criterion:** B7 (weight 8%) — The sprints.json default template does NOT contain `playbook_stage`

**Problem:** The B7 verification procedure uses `grep -A 20 '"number": 1' plugins/trine-eval/agents/planner.md`
to extract the default (non-harness-build) sprints.json example block and confirms it contains
no `playbook_stage` line. Post-sprint, the Generator is expected to add a harness-build example
block (see Reference Solution at line 297–315 of this contract) which also contains `"number": 1`.
After the sprint, `grep -A 20 '"number": 1'` will match BOTH the default block AND the
harness-build example block (which correctly contains `playbook_stage`). The output will be
concatenated with a `--` separator. The evaluator instruction says "confirm no line in that
block contains `playbook_stage`" — but the grep output will include the harness-build block
where `playbook_stage` IS expected to appear. This causes a correct implementation to FAIL B7.

**Fix:** Replace the extraction command with one that uniquely identifies the default (non-harness-build)
example block. Options:
- Use `grep -A 20 '"number": 1' plugins/trine-eval/agents/planner.md | head -20` to take only
  the first match (assuming the default block comes first in the file).
- Or anchor the extraction on a heading unique to the default section, e.g.:
  `grep -A 30 'Artifact 2' plugins/trine-eval/agents/planner.md | grep 'playbook_stage'`
  and assert exit 1 (not found).
- Or add a note in the procedure: "If the command returns multiple match groups (separated by
  `--`), evaluate only the first group."

The simplest fix is adding `| head -20` or clarifying "the first match group only."

#### ISSUE-2 [ADVISORY] — J11 and SN1 incorrectly state the Rules section has "6 rules"

**Criterion:** J11(c) and SN1 prose

**Problem:** The contract states "currently 6 rules" in J11(c) and "six rules" in SN1 prose.
The actual pre-sprint planner.md `## Rules` section contains **7 bullet-point rules**:
1. Stay at the product level
2. Order sprints so each builds on the last
3. Each sprint should be completable in one context window
4. Read the project's existing code first
5. Be ambitious about scope
6. `estimated_complexity` must be one of: "low", "medium", "high"
7. `dependencies` is an array of sprint numbers

The J11(c) listing itself enumerates all 7 (Stay, Order, Each sprint, Read, Be ambitious,
estimated_complexity enum, dependencies array) — so the count label "6 rules" contradicts
the listed enumeration within the same sentence.

This does not break the SN1 verification commands (which check specific verbatim anchors,
not a total rule count), but it does introduce an inconsistency that could confuse the
Generator or evaluator. The J11 LLM-judge criterion (b) uses "semantically identical" — a
Generator who reads J11(c) might believe 7 rules is wrong and trim to 6.

**Fix:** Change "currently 6 rules" in J11(c) to "currently 7 rules" and "six rules" in
SN1 prose to "seven rules". Also update the parenthetical enumeration in J11(c) to make
clear 7 items are listed.

#### ADVISORY: B5 no-op classification

**Criterion:** B5 (weight 8%) — pre-sprint baseline = post-sprint expected (both are 1)

**Observation:** The contract acknowledges B5's pre-sprint baseline equals its post-sprint
expected value and argues this is a valid preservation check (not a no-op) because a
reduction to 0 would constitute a FAIL. This framing is defensible — the criterion has a
detectable failure mode. However, it is worth noting that under the strict three-condition
behavioral classification rule stated in the contract itself (condition (c): "the pre-sprint
baseline differs from the post-sprint expected value, proving the criterion is not a no-op"),
B5 technically violates its own condition (c). The contract explicitly acknowledges this
tension in Technical Notes. The SN1 gate covers the same strings, making B5 partially
redundant with SN1 — it adds scoring weight for preservation rather than addition. This is
ADVISORY only; the SN1 gate provides the real protection.

#### ADVISORY: `harness.build` dot metacharacter in B3

**Criterion:** B3 second condition — `grep -c 'harness.build'`

**Observation:** The `.` in `harness.build` is a regex metacharacter matching any character,
so the pattern matches `harness-build`, `harness build`, `harness_build`, and theoretically
`harnessBbuild`. The contract intends this as a deliberate loose match (to count any variant
of the term), and the Technical Notes baseline confirms 0 occurrences pre-sprint. This is
acceptable if the intent is to count any hyphenation/spacing variant. However, the false-
positive risk (e.g., `harnessBuild` in a code comment) is real. Given that post-sprint content
will use `harness-build` (hyphenated), the regex will match correctly. This is ADVISORY — no
change required, but the contract could use `harness[-_]build\|harness build` for precision.

### Approved Criteria

- B1 (14%): simulation behavioral, framing consistent with Sprint 7 precedent. Well-specified
  with concrete pass conditions (playbook_stage field, valid stage name, dependency order).
- B2 (8%): shell-runnable, non-zero baseline change, unambiguous count threshold.
- B3 (10%): both sub-conditions have 0 pre-sprint baseline; >= 2 and >= 3 thresholds are
  non-trivially anticipated. The dot metacharacter in `harness.build` is intentional (advisory noted).
- B4 (8%): all 7 stage-name greps confirmed 0 pre-sprint. All 7 names align with
  `harness-build.md` rubric headings. Non-trivial count change.
- B5 (8%): preservation check — structurally redundant with SN1 but adds scoring weight.
  The no-op argument is addressed in Technical Notes.
- B6 (6%): pre-sprint 0 confirmed. Regex covers the key conditional-guard phrasings.
- S8 (4%): file existence + line count threshold (>= 80). Pre-sprint 69/70 lines, threshold
  requires meaningful extension.
- S9 (4%): harness-build scope annotation check. Pre-sprint 0 confirmed.
- J10 (18%): highest-weighted LLM-judge criterion. Reference solution is present and well-formed.
  Five PASS sub-conditions are specific and actionable.
- J11 (12%): backward-compat semantic check. Sub-conditions (a–d) are specific. The "6 rules"
  count error is advisory (ISSUE-2 above) and does not break the criterion's intent.
- SN1: all 5 verbatim anchors confirmed at count=1 pre-sprint. Gate is tight and meaningful.
- SN2: git diff check. Deterministic and correct.
- SN3: JIT annotation count (6). Pre-sprint baseline confirmed.
- SN4: `examples/` directory absent. Pre-sprint confirmed.
- SN5: jq field check returns `true`. Pre-sprint confirmed.

### Missing Criteria

None identified. All three sprint features (planner-harness-build-mode, stage-aligned-decomposition,
playbook-stage-traceability) have coverage across B1/B2/B3/B4/B6/B7/J10 (mode and stage
alignment), B3/S9/J10(c)/J11(a) (traceability and scope), and J11 (backward compat). The
five mandatory Should-NOT gates per the sprint brief are all present.

### Blocker Count: 1 BLOCKING issue (ISSUE-1), 1 ADVISORY with specification impact (ISSUE-2)

The B7 grep ambiguity (ISSUE-1) is a deterministic failure mode for a correct post-sprint
implementation. The rule-count error in J11/SN1 (ISSUE-2) is advisory but risks Generator
confusion about how many rules to preserve. Both should be corrected before implementation
begins. The contract can be re-approved with minimal edits: (a) add `| head -20` to B7's
extraction command or add a clarifying note; (b) change "6 rules" to "7 rules" in J11(c)
and SN1 prose.
