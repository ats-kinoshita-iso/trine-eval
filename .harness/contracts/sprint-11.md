# Sprint 11 Contract: End-to-End Ephemeral Dogfood Validation (Phase 2)

## What I Will Build

Produce `.harness/dogfood-findings.md` — a structured markdown report documenting an
ephemeral run of `/harness-kickoff` with a `harness-build` prompt against a temporary
directory (created with `New-Item -ItemType Directory -Path "$env:TEMP\dogfood-$(Get-Random)"`
on Windows or `mktemp -d` on POSIX). The tmp directory is discarded after the run; no
`examples/` directory is created in this repo. The report captures the kickoff prompt used,
excerpts of the resulting `spec.md` and `sprints.json`, behavioral observations from the
kickoff run, scoring against each of the seven harness-build rubric dimensions, verification
that the HB001 loop-termination trap criterion appears in the produced fixture's failure
catalog or spec, and a calibration verdict (PASS / PARTIAL / FAIL with named issues). This
is a single-round dogfood: if the run PASSes, that is documented; if it FAILs or is PARTIAL,
the specific failures are documented as calibration signals for the sprint, not grounds to retry.

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `behavioral` (execution-verified), `structural` (artifact-inspected), or
`llm-judge` (reading-comprehension). Weights must sum to 100% across all success criteria.

**Behavioral coverage:** Sprint 11's primary deliverable is `.harness/dogfood-findings.md` —
a markdown report file. The file is machine-readable, and many structural properties of its
contents are shell-verifiable via `grep`. Following the Sprint 8 and Sprint 10 precedents
(where `jq`/`grep` invocations on static artifacts were classified as behavioral because a
command runs, an exit code and output constitute an observable verdict, and the pre-sprint
baseline differs from the post-sprint expected value), `grep` invocations against the produced
report qualify as behavioral when: (a) the command is runnable in the evaluator's shell,
(b) the expected output is a specific integer or string — not just "non-zero", and (c) the
pre-sprint baseline differs from the post-sprint expected value. The report does not exist
pre-sprint (all counts return 0 / file-absent), so any post-sprint positive count is
non-trivially non-zero.

B1 is "simulation behavioral" — the evaluator traces the kickoff harness-build detection
branch and the resulting spec/sprints shapes by reading the dogfood findings report (which
quotes the produced artifacts), constructing the expected behavior, and verifying the report's
behavioral observations match. B2–B6 are shell-command behavioral (grep invocations with
specific expected content against `.harness/dogfood-findings.md`).

Total behavioral weight target: ≥ 60%.

### Behavioral (execution-verified)

1. **Kickoff harness-build detection trace matches planner harness-build mode** [weight: 16%]:
   Simulate the kickoff run by reading `.harness/dogfood-findings.md`: (a) Locate the section
   documenting the kickoff prompt used. (b) Locate the section documenting the resulting
   `spec.md` shape — verify the report quotes a product vision, feature list, and at least one
   success criterion from the produced spec. (c) Locate the section documenting the resulting
   `sprints.json` shape — verify the report quotes at least one sprint entry with a
   `playbook_stage` field whose value is one of the seven valid stage names from
   `rubrics/harness-build.md` (Control Plane & Agentic Loop, Tool Registry & Sandboxing,
   Projection & Planning, Skills & Instruction Execution, Observation & Monitoring, External
   Affordances, Governance & Human Oversight). (d) Verify the report's behavioral observations
   section notes that the planner produced a stage-aligned sprint decomposition consistent
   with the harness-build mode in `plugins/trine-eval/agents/planner.md`. The criterion PASSes
   when the evaluator can construct, from the dogfood-findings.md report alone, a representative
   `sprints.json` fragment with at least two sprint entries with valid `playbook_stage` values
   in dependency order. The evaluator must quote the relevant sections from the report as evidence.

2. **dogfood-findings.md contains the ephemeral tmp directory path** [weight: 8%]:
   Run `grep -c 'TEMP\|tmp\|/tmp\|dogfood-' .harness/dogfood-findings.md` and assert count >= 1.
   The report must record the tmp directory path or name used for the ephemeral kickoff run.
   Pre-sprint baseline: file absent (count would be 0 or error). Post-sprint: >= 1.
   PASS when count >= 1.

3. **dogfood-findings.md contains the kickoff prompt used** [weight: 8%]:
   Run `grep -ci 'kickoff prompt\|harness.build prompt\|prompt used\|prompt:' .harness/dogfood-findings.md`
   and assert count >= 1. The report must document the exact prompt passed to `/harness-kickoff`.
   Pre-sprint baseline: file absent. Post-sprint: >= 1. PASS when count >= 1.

4. **dogfood-findings.md contains per-dimension rubric scoring** [weight: 10%]:
   Run the following 7 greps, each against `.harness/dogfood-findings.md`, and assert each
   returns count >= 1:
   ```
   grep -c 'Control Plane' .harness/dogfood-findings.md
   grep -c 'Tool Registry' .harness/dogfood-findings.md
   grep -c 'Projection' .harness/dogfood-findings.md
   grep -c 'Skills.*Instruction\|Instruction.*Skills' .harness/dogfood-findings.md
   grep -c 'Observation.*Monitoring\|Monitoring.*Observation' .harness/dogfood-findings.md
   grep -c 'External Affordances' .harness/dogfood-findings.md
   grep -c 'Governance' .harness/dogfood-findings.md
   ```
   Pre-sprint baseline: file absent (all 0). Post-sprint: all 7 >= 1. PASS when all 7 conditions hold.
   This confirms the report scores the ephemeral fixture against all seven harness-build rubric
   dimensions.

5. **dogfood-findings.md references the HB001 loop-termination trap** [weight: 10%]:
   Run `grep -ci 'HB001\|loop termination\|max_steps\|loop.bound\|loop bound' .harness/dogfood-findings.md`
   and assert count >= 1. The report must document whether the ephemeral fixture demonstrates
   loop-termination coverage — either positively (the produced spec or sprints.json includes a
   max_steps or loop-bound criterion derived from the HB001 trap entry) or as a PARTIAL/FAIL
   calibration signal (the trap criterion was not exercised, which itself is a finding).
   Pre-sprint baseline: file absent. Post-sprint: >= 1. PASS when count >= 1.

6. **dogfood-findings.md contains a calibration verdict** [weight: 10%]:
   Run `grep -ci 'PASS\|PARTIAL\|FAIL\|calibration verdict\|verdict' .harness/dogfood-findings.md`
   and assert count >= 1. Additionally run
   `grep -ci '^## Calibration\|^## Verdict\|Calibration Verdict\|calibration verdict' .harness/dogfood-findings.md`
   and assert count >= 1. The report must declare a top-level PASS, PARTIAL, or FAIL verdict.
   Pre-sprint baseline: file absent. Post-sprint: both counts >= 1. PASS when both conditions hold.

### Structural (artifact-inspected)

7. **dogfood-findings.md exists at the correct path** [weight: 4%]:
   Run `test -f ".harness/dogfood-findings.md"` and assert exit 0 (file exists). The file must
   be committed to the repo at exactly this path. Pre-sprint baseline: ABSENT (file does not exist).
   Post-sprint: PRESENT. PASS when exit 0.

8. **dogfood-findings.md contains all required sections** [weight: 6%]:
   Run the following 5 greps and assert each returns count >= 1:
   ```
   grep -c '^## ' .harness/dogfood-findings.md
   grep -ci 'tmp\|ephemeral\|temp' .harness/dogfood-findings.md
   grep -ci 'spec\.md\|sprints\.json' .harness/dogfood-findings.md
   grep -ci 'behavioral observation\|observations' .harness/dogfood-findings.md
   grep -ci 'rubric\|dimension\|score' .harness/dogfood-findings.md
   ```
   Pre-sprint baseline: file absent (all 0). Post-sprint: all 5 >= 1. The report must have at
   least one `##`-level section heading, reference the tmp/ephemeral context, reference the
   produced spec.md and sprints.json, include behavioral observations, and include rubric scoring.
   PASS when all 5 conditions hold.

9. **No examples/ directory exists at repo root** [weight: 4%]:
   Run `test -d "examples"` and assert non-zero exit (ABSENT). This is also a Should-NOT gate
   (SN1) — this criterion overlaps with SN1 and adds scoring weight for the positive artifact
   check. Pre-sprint baseline: ABSENT (confirmed). PASS when `test -d "examples"` returns
   non-zero exit.

### LLM-as-judge (reading-comprehension)

10. **Report quality: findings are complete, structured, and evidence-grounded** [weight: 20%]:
    Read the full `.harness/dogfood-findings.md`. PASS requires ALL of the following:
    (a) **Sectioning:** The report contains clearly delineated sections for at minimum: (1) tmp
    directory path used, (2) kickoff prompt used, (3) resulting spec.md shape (quoted excerpts
    — NOT the full file), (4) resulting sprints.json shape (quoted excerpts showing at least one
    `playbook_stage` field), (5) behavioral observations, (6) per-dimension rubric scoring against
    all 7 harness-build dimensions, and (7) calibration verdict.
    (b) **Evidence standard:** The spec.md and sprints.json sections quote actual excerpts from
    the ephemeral run output — not paraphrases or synthetic examples. The quotes are clearly
    delimited (code blocks or blockquotes). The evaluator must be able to read those excerpts
    and determine whether the produced artifacts align with the harness-build planner mode.
    (c) **Rubric scoring specificity:** Each of the 7 rubric dimensions is scored with at least
    a numeric score (e.g., "3/5") OR a qualitative rating (e.g., "PASS", "PARTIAL", "FAIL")
    AND a one-sentence justification citing specific evidence from the ephemeral fixture (not a
    generic statement). Dimensions that cannot be assessed because the fixture is minimal must
    be explicitly noted as "Not assessable — minimal fixture" rather than left blank.
    (d) **Calibration verdict:** The report declares a top-level verdict (PASS / PARTIAL / FAIL)
    and — if PARTIAL or FAIL — names at least one specific issue with a proposed remediation or
    note that it is documented as a calibration signal.
    (e) **HB001 loop-termination coverage:** The report explicitly addresses whether the
    ephemeral fixture exercised the loop-termination trap (HB001 from
    `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`):
    either confirming the fixture includes a numeric `max_steps` bound or similar, or noting
    its absence as a calibration finding. A report that does not address HB001 at all fails
    this sub-condition.
    (f) **No committed examples:** The report explicitly notes that the tmp directory was
    discarded and that no `examples/` directory was created in the repo. This is the ephemeral
    constraint declaration.

11. **Kickoff routing correctness: planner produced harness-build-aligned output** [weight: 4%]:
    Read the behavioral observations section and the sprints.json excerpt in
    `.harness/dogfood-findings.md`. PASS requires:
    (a) The report confirms the kickoff's planner subagent activated harness-build mode — either
    by detecting a `harness-build` keyword in the prompt or by the planner reading/writing
    `project_type: harness-build` to config.json.
    (b) The sprints.json excerpt shows at least two sprint entries in stage-dependency order
    (e.g., sprint 1 = Control Plane & Agentic Loop before sprint N = Governance & Human Oversight).
    (c) The report does not claim kickoff succeeded if the planner failed to produce a
    stage-aligned decomposition — failures are documented, not masked.

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT create an `examples/` directory at the repo root** [weight: gate]: Phase 2's
   ephemeral constraint prohibits committing permanent example fixtures. The dogfood run uses
   a tmp directory (discarded after the run); no `examples/` directory is committed.
   Verify: `test -d "examples"` returns non-zero exit (ABSENT).
   Pre-sprint baseline: ABSENT (confirmed by Sprint 10 SN4 gate, also confirmed current).

2. **Should NOT modify any prior sprint's approved markdown contract** [weight: gate]: The
   content of all prior approved contracts must be byte-for-byte identical to their HEAD state.
   Verify all of the following produce empty output (no diff):
   ```
   git diff HEAD -- .harness/contracts/sprint-07.md
   git diff HEAD -- .harness/contracts/sprint-08.md
   git diff HEAD -- .harness/contracts/sprint-09.md
   git diff HEAD -- .harness/contracts/sprint-10.md
   ```
   PASS when all four diffs are empty.

3. **Should NOT regress Sprint 6 JIT annotations in harness-kickoff SKILL.md** [weight: gate]:
   The six `<!-- Context scope at this step: ... -->` comment blocks added in Sprint 6 must
   remain intact. Verify:
   ```
   grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   ```
   assert count >= 6. Pre-sprint baseline: 6 (Steps 1, 2, 2b, 3, 4, and 5 — confirmed by
   Sprint 10 SN3 gate evaluation).

4. **Should NOT remove or alter the core fields in `.harness/config.json`** [weight: gate]:
   The fields `project_type`, `rubric`, `max_retries`, and `governance.enabled` must retain
   their current values. Verify:
   ```
   jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json
   ```
   must output `true`. Pre-sprint baseline: all four fields confirmed at those values (Sprint 10
   SN5 gate passed; config.json unchanged).

5. **Should NOT modify read-only inputs to this sprint's dogfood run** [weight: gate]:
   The following files are read-only inputs consumed by the ephemeral kickoff — they must not
   be modified by this sprint's implementation:
   `plugins/trine-eval/agents/planner.md`,
   `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md`, and
   `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`.
   Verify:
   ```
   git diff HEAD -- plugins/trine-eval/agents/planner.md
   git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md
   git diff HEAD -- plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json
   ```
   All three commands must produce empty output. PASS when all three diffs are empty.

## Reference Solutions

**Criterion J10 — Report quality: findings are complete, structured, and evidence-grounded
(highest-weighted LLM-judge criterion, 20%):**

The following illustrates the required structure and quality of `.harness/dogfood-findings.md`.
The exact prose, scores, and quotes will differ (they depend on the actual ephemeral run output),
but the structural elements below must be present:

```markdown
# Dogfood Findings: Ephemeral harness-build Kickoff Validation

**Sprint:** 11
**Date:** 2026-06-01
**Calibration Verdict:** PARTIAL — loop-termination criterion HB001 not surfaced in spec
  success criteria; documented as calibration signal.

## 1. Ephemeral Setup

Tmp directory created: `C:\Users\akino\AppData\Local\Temp\dogfood-1749381234`
(or `/tmp/dogfood-abc123` on POSIX). Directory discarded after run. No `examples/`
directory created in the trine-eval repo root.

## 2. Kickoff Prompt Used

> "Initialize an eval-driven development harness for a minimal agent runtime harness.
> The harness should have an agentic loop with max_steps bound, a tool registry with
> sandbox declaration, and a governance escalation policy. Use harness-build project type."

## 3. Resulting spec.md (excerpts)

```markdown
# Product Specification: Minimal Agent Runtime Harness

## Product Vision
A minimal agent runtime harness implementing the three UNCONDITIONAL gate requirements:
loop termination bounds, tool registry with sandboxing, and governance escalation policy.
...

## Phase 1 Success Criteria
1. The harness declares `max_steps: 50` in its loop config (satisfies Loop Termination gate)
2. The tool registry entry for code execution declares at least two isolation dimensions
3. An escalation policy document lists action categories requiring human review
```

## 4. Resulting sprints.json (excerpts)

```json
{
  "sprints": [
    {
      "number": 1,
      "title": "Control plane and agentic loop with max_steps bound",
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
    },
    {
      "number": 5,
      "title": "Governance and human oversight escalation policy",
      "features": ["escalation-policy", "approval-gates", "audit-trail"],
      "estimated_complexity": "medium",
      "dependencies": [1, 2, 3, 4],
      "playbook_stage": "Governance & Human Oversight"
    }
  ]
}
```

## 5. Behavioral Observations

- The planner subagent correctly detected `harness-build` mode from the prompt keywords
  ("agentic loop", "tool registry", "governance escalation policy").
- `project_type: harness-build` was written to the tmp dir's `config.json`.
- Sprint ordering follows the playbook dependency order: Control Plane (1) → Tool Registry (2)
  → ... → Governance (5). PASS.
- HB001 trap (loop termination): The spec's success criteria includes a numeric `max_steps: 50`
  reference — the loop-termination criterion is exercised. PASS.
- HB005 trap (sandboxing): The sprints.json Sprint 2 features include `sandbox-config` —
  sandboxing criterion is addressed. PASS.

## 6. Per-Dimension Rubric Scoring

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Control Plane & Agentic Loop (20%) | 3/5 | max_steps declared in spec; state transitions not modeled |
| Tool Registry & Sandboxing (18%) | 2/5 | sandbox-config feature listed; no isolation dimensions specified |
| Projection & Planning (12%) | 1/5 | No planning subsystem in spec — minimal fixture |
| Skills & Instruction Execution (15%) | Not assessable — minimal fixture | |
| Observation & Monitoring (12%) | Not assessable — minimal fixture | |
| External Affordances (8%) | Not assessable — minimal fixture | |
| Governance & Human Oversight (15%) | 3/5 | Escalation policy sprint planned; no approval mechanism |

Hard threshold gates:
- Loop Termination & Bounds: PASS (max_steps in spec)
- Sandboxing: PARTIAL — declared as feature, dimensions unspecified
- Governance Placement: PARTIAL — policy sprint planned but no enforcement

## 7. Calibration Verdict

**PARTIAL** — The harness-build planner mode activated correctly and produced a
stage-aligned sprint decomposition with `playbook_stage` fields. The loop-termination
criterion (HB001) was exercised in the spec. However, two of the three UNCONDITIONAL
gates scored only PARTIAL because the ephemeral fixture was intentionally minimal.

Named issues:
1. Sandboxing (UNCONDITIONAL gate): isolation dimensions not specified in the tool registry
   sprint. Calibration signal: the harness-build rubric's HB005 trap criterion is not yet
   surfacing isolation-dimension requirements into generated success criteria.
2. Governance placement (UNCONDITIONAL gate): the escalation policy is planned but the
   approval mechanism is absent from sprint success criteria.

These are calibration signals — not implementation bugs in trine-eval. The planner and rubric
are functioning; the ephemeral fixture's minimal scope limits how deeply the traps are exercised.
```

**Key quality markers:** All 7 required sections are present. spec.md and sprints.json excerpts
are quoted (not paraphrased). All 7 rubric dimensions are scored or explicitly noted as
"Not assessable — minimal fixture". HB001 is addressed explicitly. The calibration verdict is
PASS/PARTIAL/FAIL with named issues. The ephemeral constraint (no examples/) is declared.
The harness-build planner mode activation is confirmed with evidence.

## Out of Scope

- **Rubric decision README (Sprint 12):** `plugins/trine-eval/skills/eval-rubric/rubrics/README.md`
  explaining when to use `eval-harness` vs `harness-build` is NOT part of this sprint.
- **Modifying harness source files:** This sprint does NOT modify `plugins/trine-eval/agents/planner.md`,
  `plugins/trine-eval/skills/harness-kickoff/SKILL.md`,
  `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md`, or
  `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`.
  Those files are read-only inputs to the dogfood run.
- **Committing example fixtures:** No `examples/` directory and no ephemeral tmp directory
  contents are committed. Only `.harness/dogfood-findings.md` is committed.
- **Multiple kickoff rounds:** This is a single-round dogfood. FAIL outcomes are documented
  as calibration signals, not grounds for retry.
- **Back-filling previous sprints' tasks.json:** tasks.json emission for Sprint 11 is the
  standard Step 1d post-approval workflow, not an implementation deliverable.
- **Modifying `.harness/sprints.json`, `.harness/spec.md`, or `.harness/config.json`:** These
  are the active harness files for the trine-eval repo itself — they are NOT the ephemeral
  fixture files produced during the dogfood run.
- **Phase 1.6 governance hardening (Sprint 13):** The bidirectional council-check gates are
  NOT part of this sprint.

## Technical Notes

**Behavioral coverage (≥ 60% target):**

Sprint 11 delivers a single markdown report file (`.harness/dogfood-findings.md`) as its
primary artifact. No runnable binary, hook listener, or library function is introduced.
However, the report is machine-readable, and its required content sections map to shell-verifiable
`grep` invocations. The behavioral classification follows the Sprint 8 `jq` precedent and the
Sprint 10 `grep` precedent:

`grep` invocations on `dogfood-findings.md` qualify as behavioral (not structural) when:
1. A shell command is run (`grep` or `grep -c`).
2. A specific integer output is observed (count >= N, not just non-zero exit).
3. The pre-sprint baseline differs from the post-sprint expected value — the file does not
   exist pre-sprint, so any positive count is non-trivially non-zero.

Under this classification:
- B1: simulation behavioral (kickoff trace from report content, analogous to Sprint 7/10 B1).
  The evaluator reads the report and constructs the expected sprints.json fragment — no shell
  entry point exists for the kickoff skill itself. Classified behavioral following Sprint 7/10 precedent.
- B2: pre-sprint count = 0 (file absent), post-sprint >= 1. Shell-runnable, specific count. Behavioral.
- B3: pre-sprint count = 0, post-sprint >= 1. Shell-runnable, specific count. Behavioral.
- B4: pre-sprint all 0, post-sprint all >= 1 (7 conditions). Shell-runnable, specific counts. Behavioral.
- B5: pre-sprint count = 0, post-sprint >= 1. Shell-runnable, specific count. Behavioral.
- B6: pre-sprint count = 0, post-sprint >= 1 (both sub-conditions). Shell-runnable. Behavioral.

Weight breakdown:
- Behavioral: B1 (16%) + B2 (8%) + B3 (8%) + B4 (10%) + B5 (10%) + B6 (10%) = **62%**
- Structural: S7 (4%) + S8 (6%) + S9 (4%) = **14%**
- LLM-as-judge: J10 (20%) + J11 (4%) = **24%**
- Total: 62% + 14% + 24% = **100%** ✓
- Behavioral coverage: 62% ≥ 60% floor ✓

**Ephemeral tmp directory convention:**

The dogfood run creates a temporary directory, runs `/harness-kickoff` against it, reads the
produced artifacts (to document excerpts in the findings report), then discards the tmp directory.
The findings report documents the tmp directory path used.

Windows recipe (PowerShell):
```powershell
$tmpDir = New-Item -ItemType Directory -Path "$env:TEMP\dogfood-$(Get-Random)" -Force
# run kickoff in $tmpDir
# read $tmpDir/.harness/spec.md and $tmpDir/.harness/sprints.json for excerpts
Remove-Item -Recurse -Force $tmpDir
```

POSIX recipe (bash):
```bash
tmpDir=$(mktemp -d /tmp/dogfood-XXXXXX)
# run kickoff in $tmpDir
# read $tmpDir/.harness/spec.md and $tmpDir/.harness/sprints.json for excerpts
rm -rf "$tmpDir"
```

Because the ephemeral kickoff runs in a separate tmp directory, the trine-eval repo's own
`.harness/` files (spec.md, sprints.json, config.json, contracts/) are untouched. Only
`.harness/dogfood-findings.md` is written to the trine-eval repo.

**HB001 loop-termination trap — Phase 2 Success Criterion 9:**

Phase 2 spec.md Success Criterion 9 requires: "The harness-build rubric grades a deliberately
minimal ephemeral harness fixture (no permanent `examples/` directory) with at least one
trap-derived behavioral criterion exercising loop termination."

HB001 in `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
is the canonical loop-termination trap entry:
- `id`: "HB001"
- `rubric_dimension`: "Control Plane & Agentic Loop"
- `success_criteria`: "The harness config or control plane documentation declares a numeric
  max_steps value >= 1 AND a numeric max_tokens value >= 1."

Sprint 11 satisfies Phase 2 criterion 9 by: (a) running the ephemeral kickoff with a
harness-build prompt that includes loop-bounding concepts, (b) documenting in the findings
report whether the produced spec and sprints exercised the HB001 criterion (B5 verifies this),
and (c) scoring the ephemeral fixture's Control Plane & Agentic Loop dimension against the
rubric (B4 and J10 verify this). The findings report documents both a PASS case (loop bound
present in spec) and a calibration signal if absent — either way, the rubric dimension was
applied to the ephemeral fixture.

**Pre-sprint baselines (no-op detection, all verified against current repo):**

- `test -f ".harness/dogfood-findings.md"` → ABSENT (file does not exist). S7 is not a no-op.
- `grep -c 'Control Plane' .harness/dogfood-findings.md` → error/0 (file absent). B4 is not a no-op.
- `grep -c 'HB001' .harness/dogfood-findings.md` → error/0 (file absent). B5 is not a no-op.
- `test -d "examples"` → ABSENT (non-zero exit). SN1 baseline confirmed.
- `git diff HEAD -- .harness/contracts/sprint-07.md` → empty. SN2 baseline confirmed.
- `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` → 6. SN3 baseline confirmed.
- `jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json` → `true`. SN4 baseline confirmed.
- `git diff HEAD -- plugins/trine-eval/agents/planner.md` → empty. SN5 baseline confirmed.

**Kickoff routing note:**

The dogfood kickoff prompt must include keywords that activate the planner's harness-build mode:
terms like "agentic loop", "tool registry", "harness-build", "agent runtime harness", or
"governance escalation" trigger the dual-signal detection in `plugins/trine-eval/agents/planner.md`
(lines 79-90 per Sprint 10 implementation). The findings report must document which detection
signal fired. A prompt that does not activate harness-build mode would produce a generic
`sprints.json` without `playbook_stage` fields — that outcome is itself a valid calibration
finding (PARTIAL or FAIL verdict) and should be documented as such.

**Single-round rationale:**

The sprint notes specify "single round; if PASS, document; if FAIL, document as calibration
signal." This means: the Generator runs the ephemeral kickoff once. If the planner produces
stage-aligned output with `playbook_stage` fields, documents HB001 coverage, and all three
UNCONDITIONAL gates are addressed — verdict is PASS. If one or more UNCONDITIONAL gates are
absent from the fixture, or the planner fails to activate harness-build mode — the specific
failures are documented in the findings report as calibration signals (labeled issues under
the PARTIAL or FAIL verdict). In either case, `.harness/dogfood-findings.md` is committed.
The single-round constraint prevents scope creep into iterative re-runs that would balloon
the sprint.

**File paths for Sprint 11:**

- New file (deliverable): `.harness/dogfood-findings.md`
- Ephemeral files (discarded, not committed): `<tmp>/.harness/spec.md`, `<tmp>/.harness/sprints.json`, `<tmp>/.harness/config.json`
- Read-only inputs: `plugins/trine-eval/agents/planner.md`, `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md`, `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
- Protected files: all `.harness/contracts/sprint-*.md`, `harness-kickoff/SKILL.md`, `.harness/config.json`

## Evaluator Review

**Status: APPROVED**

### Review Summary

All seven checklist items passed. Detailed findings follow.

---

### 1. Testability — Verification Commands on Windows + Git Bash + PowerShell

**B2 (tmp path grep):**
```
grep -c 'TEMP\|tmp\|/tmp\|dogfood-' .harness/dogfood-findings.md
```
The pattern `TEMP\|tmp\|/tmp\|dogfood-` uses POSIX alternation syntax. Under Git Bash this
works correctly. Under PowerShell's native `grep` (if invoked as a cmdlet alias) it would fail
— but since the harness evaluator always runs through Git Bash, this is acceptable. The pattern
is unambiguous: any of the four substrings suffice for a count >= 1. **No issue.**

**B3 (kickoff prompt grep):**
```
grep -ci 'kickoff prompt\|harness.build prompt\|prompt used\|prompt:' .harness/dogfood-findings.md
```
The pattern `harness.build` uses an unescaped `.` that matches any character — intended to
match both `harness-build` and `harness_build`. This is intentional fuzzy matching and will
not produce false positives in this context (the file is a findings report, not arbitrary
code). The four alternatives are broad enough that a compliant report will always match at
least one. **No issue.**

**B4 (7-dimension greps):**
The alternation patterns like `'Skills.*Instruction\|Instruction.*Skills'` and
`'Observation.*Monitoring\|Monitoring.*Observation'` are correct POSIX regex alternatives and
will work in Git Bash. The seven greps target exact rubric dimension names from
`harness-build.md` and will not false-positive on unrelated text. **No issue.**

**B6 (calibration verdict greps):**
```
grep -ci 'PASS\|PARTIAL\|FAIL\|calibration verdict\|verdict' .harness/dogfood-findings.md
```
The first pattern is intentionally broad — "PASS", "PARTIAL", or "FAIL" will appear in
any rubric-scoring table. However the second sub-condition anchors to a section header:
```
grep -ci '^## Calibration\|^## Verdict\|Calibration Verdict\|calibration verdict'
```
The `^` anchors work correctly in grep line-by-line mode (not multiline). Because `grep`
processes each line independently by default, `^##` matches lines starting with `##`. This is
correct and safe on both POSIX and Git Bash. **No issue.**

**SN2 (prior contract diffs):**
The command `git diff HEAD -- .harness/contracts/sprint-07.md` checks uncommitted working-tree
changes only. This correctly detects mid-sprint modifications to prior contracts. Verified
against current repo: all four diffs are empty. **Confirmed working.**

**SN4 (config jq):**
```
jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json
```
Verified: outputs `true` against the current repo. **Confirmed working.**

---

### 2. Behavioral Coverage — ≥ 60% Rule

Weights confirmed by arithmetic:
- B1 (16%) + B2 (8%) + B3 (8%) + B4 (10%) + B5 (10%) + B6 (10%) = **62%**
- Structural: S7 (4%) + S8 (6%) + S9 (4%) = 14%
- LLM-judge: J10 (20%) + J11 (4%) = 24%
- Total = 100% ✓

The behavioral classification follows the Sprint 8/10 precedent for `grep` on static
machine-readable artifacts: (a) a shell command runs, (b) the expected output is a specific
integer (count >= N), (c) the pre-sprint baseline is 0 (file absent). All three conditions
confirmed for B2–B6.

B1 is the "simulation behavioral" category from Sprint 10 — the evaluator reads the findings
report and constructs the expected sprints.json fragment rather than running a binary. This
classification was ratified in Sprint 10's approved contract and matches the same reasoning
there (planner.md is also a static artifact requiring trace simulation).

**Behavioral coverage: 62% ≥ 60% floor. Confirmed.**

---

### 3. Weight Sum

Sum of all criterion weights:
16 + 8 + 8 + 10 + 10 + 10 + 4 + 6 + 4 + 20 + 4 = **100%** ✓

---

### 4. Should-NOT Gates — Specificity and Scope

**SN1** — `test -d "examples"` returns non-zero (ABSENT). This is the identical pattern used
by Sprint 10 SN4. Pre-sprint baseline confirmed ABSENT. Not over-broad: any correct
implementation that avoids creating `examples/` will pass; any that creates it will fail.
**Specific and correct.**

**SN2** — Four explicit `git diff HEAD` commands against sprint-07 through sprint-10. Correct
breadth: covers all contracts that could be regressed by Sprint 11's implementation. The
command syntax is valid Git Bash. Empty-output check for four specific files is deterministic.
**Specific and correct.**

**SN3** — `grep -c '<!-- Context scope at this step:'` asserts count >= 6. Pre-sprint baseline
confirmed: count = 6 (verified by running the command against the current file). The SN3 prose
correctly states "six ... comment blocks added in Sprint 6" and lists Steps 1, 2, 2b, 3, 4,
and 5. This matches the actual annotation count (6). **Specific and correct.**

Note: The contract's SN3 description says "six `<!-- Context scope at this step: ... -->`
comment blocks" and "count >= 6". The harness-kickoff SKILL.md currently has exactly 6 such
annotations (confirmed by `grep -c`). The `>= 6` threshold is correct — it would not fire on
a compliant implementation that adds annotations (count would exceed 6) but would fire if any
were removed (count < 6). **No regression issue.**

**SN4** — jq check for four config fields. Pre-sprint baseline verified: outputs `true`.
**Specific and correct.**

**SN5** — Three `git diff HEAD` commands against the read-only inputs. Correct and specific.
Pre-sprint baseline confirmed: all three produce empty output. **Specific and correct.**

---

### 5. Phase 2 Success Criterion 9 Traceability

spec.md Phase 2 Success Criterion 9: "The harness-build rubric grades a deliberately minimal
ephemeral harness fixture (no permanent `examples/` directory) with at least one trap-derived
behavioral criterion exercising loop termination."

This is addressed by multiple criteria:
- **B5** requires the findings report to reference HB001/loop-termination explicitly (grep on
  'HB001|loop termination|max_steps|loop.bound|loop bound'). A positive result confirms the
  report documents whether the ephemeral fixture exercised the HB001 trap.
- **J10(e)** explicitly requires the report to address whether the ephemeral fixture exercised
  the loop-termination trap (HB001), either confirming it or noting its absence as a
  calibration finding.
- **J11** requires the behavioral observations section to confirm planner subagent activated
  harness-build mode and produced stage-aligned output.

The HB001 entry in `harness-build.json` confirms this is the correct canonical loop-termination
trap: `id: "HB001"`, `rubric_dimension: "Control Plane & Agentic Loop"`,
`success_criteria: "declares a numeric max_steps value >= 1 AND a numeric max_tokens value >= 1"`.

**Phase 2 Success Criterion 9 is fully traceable through B5 + J10(e). Confirmed.**

---

### 6. Single-Round Ephemeral Semantics

The contract makes the single-round constraint explicit in multiple places:
- "What I Will Build" paragraph: "This is a single-round dogfood: if the run PASSes, that is
  documented; if it FAILs or is PARTIAL, the specific failures are documented as calibration
  signals for the sprint, not grounds to retry."
- Out of Scope section: "Multiple kickoff rounds: This is a single-round dogfood. FAIL outcomes
  are documented as calibration signals, not grounds for retry."
- Technical Notes "Single-round rationale" subsection: explains the full logic explicitly.

A Generator reading this contract cannot mistake FAIL as grounds for re-running. **Confirmed.**

---

### 7. Read-Only Inputs Protection

SN5 guards `planner.md`, `harness-build.md`, and `harness-build.json` against modification via
`git diff HEAD` checks. The "Out of Scope" section also explicitly lists these files as
read-only inputs. The "File paths" section reinforces this by labeling them "Read-only inputs."

The harness-kickoff SKILL.md is not in SN5's file list but is listed in "Protected files" in
the Technical Notes section. However, SN5 is the enforcement gate — the evaluator checks the
three files listed. The kickoff SKILL.md is protected by SN3 (which guards the JIT annotations
within it) rather than by a full-file diff check. This is acceptable: if Sprint 11's
implementation modified kickoff SKILL.md in any way that removed or altered the JIT annotations,
SN3 would catch it. Arbitrary additions to kickoff SKILL.md (e.g., a comment) would not be
blocked by SN3, but the Out of Scope text ("This sprint does NOT modify
`plugins/trine-eval/skills/harness-kickoff/SKILL.md`") provides a clear negative instruction
to the Generator. This is the same protection level Sprint 10 used and is appropriate.

**Read-only inputs are protected. Confirmed.**

---

### 8. `examples/` Absence Check

SN1 uses `test -d "examples"` returning non-zero (ABSENT). This is identical to Sprint 10's
SN4 pattern. The pre-sprint baseline is confirmed ABSENT. S9 (structural criterion) also
overlaps with SN1 and adds 4% scoring weight, so the check is doubly enforced.
**Correct pattern. Confirmed.**

---

### Approved Criteria

All criteria are well-formed:

- **B1 (16%)** — Simulation behavioral, follows Sprint 10 precedent. Specific pass condition:
  evaluator can construct representative sprints.json fragment with >= 2 sprint entries in
  dependency order. Rubric standard is clear.
- **B2 (8%)** — Shell-runnable, specific count >= 1, pre-sprint baseline 0. Correct.
- **B3 (8%)** — Shell-runnable, specific count >= 1, pre-sprint baseline 0. Correct.
- **B4 (10%)** — Seven greps, each count >= 1, all pre-sprint baseline 0. Correct.
- **B5 (10%)** — Shell-runnable, specific count >= 1, pre-sprint baseline 0. HB001 traceability
  confirmed.
- **B6 (10%)** — Two sub-conditions, both count >= 1. Broad first grep is adequately anchored
  by the section-header second grep. Correct.
- **S7 (4%)** — `test -f` existence check. Correct.
- **S8 (6%)** — Five section-presence greps, each count >= 1. Correct.
- **S9 (4%)** — `test -d examples` non-zero exit. Correct. Dual enforcement with SN1.
- **J10 (20%)** — Six sub-conditions (a)–(f) covering sectioning, evidence standard, rubric
  scoring specificity, calibration verdict, HB001 coverage, and ephemeral constraint
  declaration. Reference solution provided as required for the highest-weighted LLM-judge
  criterion. Rubric is specific enough for two independent evaluators to agree.
- **J11 (4%)** — Three sub-conditions covering planner mode activation, stage-dependency order,
  and no-masking of failures. Readable and specific.
- **SN1–SN5** — All gates are specific, non-over-broad, and pre-sprint baselines confirmed.

### Missing Criteria

None identified. The contract covers: file existence (S7), file sections (S8), ephemeral
constraint (SN1/S9), kickoff prompt documentation (B3), tmp directory documentation (B2),
per-dimension rubric scoring (B4), HB001 loop-termination coverage (B5), calibration verdict
(B6), kickoff trace/behavioral observations (B1), overall report quality (J10), planner routing
correctness (J11), and all read-only input protections (SN2–SN5).

Phase 2 Success Criterion 9 is traceable (B5 + J10(e)). Single-round semantics are explicit.
Ephemeral constraint is multiply enforced. Behavioral weight floor is met (62%).

### One Advisory (Non-Blocking)

**B6 first sub-condition is very broad.** `grep -ci 'PASS\|PARTIAL\|FAIL\|calibration verdict\|verdict'`
will match on nearly any rubric-scoring table (e.g., the dimension score table in section 6
will contain "PASS" or "PARTIAL" for hard threshold gates). This is harmless because the
second sub-condition (`grep -ci '^## Calibration\|...'`) is the meaningful anchor. The
criterion PASSes only when BOTH conditions hold. The broad first grep should not produce false
negatives (it is too easy to pass), but false negatives are the wrong direction to worry
about for a gate that requires both conditions. The second sub-condition is the real guard.
**Advisory only — not a blocking issue.**
