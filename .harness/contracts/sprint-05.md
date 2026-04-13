# Sprint 05 Contract: Bootstrap, Calibration, and ACI Self-Optimization

## What I Will Build

Add three new capabilities: (1) a bootstrap-from-failures workflow for importing real failure cases as initial eval tasks (playbook Step 0-1), (2) a human calibration pathway for spot-checking evaluator grades, and (3) an ACI self-optimization mechanism where eval transcripts inform tool/skill description improvements.

## Success Criteria

### Deterministic (code-verifiable)

1. **Bootstrap skill exists** [weight: 7%]: A new skill file exists at `skills/bootstrap-failures/SKILL.md`. Verify: file exists at that path.

2. **Bootstrap skill has valid frontmatter** [weight: 5%]: The file starts with YAML frontmatter. Verify: `head -5 skills/bootstrap-failures/SKILL.md | grep -c '^---'` >= 1 AND `grep -c 'name:\|description:\|allowed-tools:' skills/bootstrap-failures/SKILL.md` >= 3.

3. **Human calibration has a dedicated section** [weight: 7%]: `agents/evaluator.md` contains a dedicated `## Human Calibration` section heading (not just incidental mentions in the hierarchy). Verify: `grep -c '## Human Calibration' agents/evaluator.md` >= 1.

4. **ACI optimization content exists in a skill definition** [weight: 7%]: A SKILL.md file contains content about tool description optimization from eval data. Verify: `grep -rci 'tool.*description.*optim\|transcript.*improv\|eval.*transcript.*feedback' skills/*/SKILL.md` >= 1.

5. **Bootstrap skill references failure sources** [weight: 5%]: The bootstrap skill mentions at least two sources of real failures. Verify: `grep -ci 'bug.*report\|support.*ticket\|manual.*test\|production.*log\|failure.*case\|incident' skills/bootstrap-failures/SKILL.md` >= 2.

6. **All skills have valid frontmatter** [weight: 4%]: All skill directories including the new one have YAML frontmatter. Verify: `grep -rl '^---' skills/*/SKILL.md | wc -l` >= 6.

### LLM-as-judge (requires reading comprehension)

7. **Bootstrap workflow is complete** [weight: 12%]: The bootstrap skill describes: (a) where to find real failure cases (at least 2 sources), (b) how to convert them into eval tasks with unambiguous success criteria, (c) a target of 20-50 initial tasks per Anthropic's guidance, and (d) how these tasks feed into the existing sprint contract workflow. PASS requires all four elements.

8. **Human calibration is actionable** [weight: 12%]: The evaluator's Human Calibration section explains: (a) when to flag criteria for human review (low-confidence LLM-judge grades, borderline cases), (b) how to record human overrides (specific file path and format), and (c) how human calibration results feed back into improving LLM grader accuracy (updating calibration examples, adjusting rubric thresholds). PASS requires all three elements.

9. **ACI self-optimization is grounded in eval data** [weight: 10%]: The optimization mechanism explains: (a) how to extract actionable feedback from eval transcripts (which tool calls failed, which descriptions were misinterpreted), (b) a concrete process for improving tool/skill descriptions based on that feedback, and (c) that improvements should be validated against held-out eval cases. PASS requires all three elements.

10. **Bootstrap integrates with existing harness** [weight: 8%]: The bootstrap skill references or creates artifacts in `.harness/` (e.g., a failure catalog file), and the kickoff or workflow skill can consume these artifacts. The integration must describe the data flow from bootstrap → harness artifacts → sprint contracts.

11. **Methodology coverage reaches 7+ of 8 steps** [weight: 13%]: Across all harness files, at least 7 of the following 8 steps are addressed by a concrete mechanism (a specific section, workflow, or tool — not just a passing mention):
    - Step 0: Start early with real failures → bootstrap skill
    - Step 1: Convert manual tests to automated → bootstrap conversion process
    - Step 2: Unambiguous tasks with reference solutions → contract template
    - Step 3: Balanced positive/negative test sets → Should-NOT criteria in contracts
    - Step 4: Stable eval environment → environment isolation in evaluator
    - Step 5: Grader hierarchy (code→LLM→human) → evaluator grading hierarchy
    - Step 6: Check transcripts → eval report review / ACI optimization
    - Step 7: Saturation monitoring → eval-summary graduation

12. **Transcript review mechanism is explicit** [weight: 10%]: At least one file contains an explicit instruction to review eval transcripts/reports for grader accuracy, not just for pass/fail results. This addresses Step 6 of the playbook ("You won't know if your graders are working well unless you read the transcripts and grades from many trials"). PASS requires the instruction to specifically target grader quality, not just sprint outcomes.

## Should-NOT Criteria

1. **Should NOT break existing skill structure**: All existing skills plus the new one must have YAML frontmatter. Verify: `grep -rl '^---' skills/*/SKILL.md | wc -l` >= 6.

2. **Should NOT remove evaluator calibration examples**: The three built-in calibration examples must remain. Verify: `grep -c 'Example:' agents/evaluator.md` >= 3.

## Reference Solutions

**Criterion 7 — Bootstrap workflow:**
```markdown
## Sources of Real Failures
1. **Bug reports** from issue trackers — each bug becomes a test case
2. **Manual test notes** — QA team's manual checks converted to automated criteria
3. **Production incidents** — post-mortems provide high-impact failure scenarios
4. **Support tickets** — user-reported issues reveal real-world edge cases

## Conversion Process
For each failure case:
1. Write a clear problem statement (the "task")
2. Define unambiguous success criteria (what "fixed" looks like)
3. Include a reference solution if one exists
4. Tag with the relevant rubric dimension

## Target
Start with 20-50 real failure cases per Anthropic's guidance.
```

**Criterion 8 — Human calibration:**
```markdown
## When to Flag for Human Review
- LLM-judge grades where confidence is below threshold
- Borderline PASS/FAIL cases where evidence is ambiguous
- First evaluation of a new rubric dimension

## Recording Overrides
Write human calibration results to `.harness/calibration/human-grades.md`:
- Original LLM grade, human grade, reasoning for disagreement

## Feedback Loop
- Disagreements become new calibration examples in the evaluator
- Systematic disagreements trigger rubric threshold adjustments
```

**Criterion 9 — ACI self-optimization:**
```markdown
## Extract Feedback from Eval Transcripts
1. Read eval reports looking for: tool calls that failed, descriptions that were misinterpreted, criteria where the grader type was wrong
2. Identify patterns across sprints

## Improvement Process
1. Paste relevant eval transcript sections into a review prompt
2. Propose description changes targeting the identified failure modes
3. Apply changes to skill/agent markdown files

## Validation
Test improved descriptions against held-out eval cases (prior sprint evals that were not used to derive the improvements) to verify the change helps.
```

**Criterion 11 — Methodology step mapping:**
| Step | Mechanism | File |
|------|-----------|------|
| 0: Start early | bootstrap-failures skill | skills/bootstrap-failures/SKILL.md |
| 1: Manual→automated | Bootstrap conversion process | skills/bootstrap-failures/SKILL.md |
| 2: Unambiguous tasks | Contract template with reference solutions | skills/sprint-contract/template.md |
| 3: Balanced tests | Should-NOT criteria section | skills/sprint-contract/template.md |
| 4: Stable environment | Environment isolation section | agents/evaluator.md |
| 5: Grader hierarchy | Grading Hierarchy (code→LLM→human) | agents/evaluator.md |
| 6: Check transcripts | Transcript review / ACI optimization | eval-summary or ACI skill |
| 7: Saturation | Saturation & Regression Graduation | skills/eval-summary/SKILL.md |

## Out of Scope

- Runtime execution of bootstrap (this sprint defines the workflow, not a script)
- Integration with external issue trackers (the skill describes manual import)
- Changes to the planner agent

## Technical Notes

- This sprint creates one new skill (bootstrap-failures) and extends existing agents/skills
- The ACI optimization can be a section in an existing skill or a new skill — implementer's choice
- Step 6 (transcript review) is partially covered by the evaluator reading eval reports; this sprint should make it more explicit
- The 8 methodology steps from the playbook are the scoring basis for criterion 11

## Evaluator Review (Round 2)

**Status:** CONDITIONAL PASS — 5 of 6 Round 1 issues resolved; 1 new issue found.

### Round 1 Issue Verification

| # | Issue | Verdict | Notes |
|---|-------|---------|-------|
| 1 | Criterion 3 was a no-op (grep matched unmodified file) | RESOLVED | Now checks for `## Human Calibration` heading, which does not exist in the current `agents/evaluator.md`. Requires new content. |
| 2 | Criterion 10 (now 11) lacked reference solution | RESOLVED | Step-to-file mapping table added (lines 103-113). All 8 steps mapped to specific mechanisms and file paths. |
| 3 | SN1 threshold was at floor | RESOLVED | Threshold is `>= 6`. Current skill count is 5. The new bootstrap-failures skill brings total to 6, so any regression (broken frontmatter or missing skill) causes failure. |
| 4 | Criterion 2 was fragile | RESOLVED | Now checks both `head -5 | grep '^---'` for frontmatter delimiters AND `grep -c 'name:\|description:\|allowed-tools:'` >= 3 for required fields. Two-part verification is robust. |
| 5 | Criterion 4 matched "aci" as substring | RESOLVED | Bare "aci" removed. New patterns (`tool.*description.*optim`, `self.*optim`, `transcript.*improv`, `eval.*transcript.*feedback`) do not match on a bare substring. |
| 6 | Criterion 8 lacked reference solution | RESOLVED | Reference solution added (lines 73-86) covering when to flag, recording overrides, and the feedback loop. |

### New Issue Found

**Issue 7 — Criterion 4 is a no-op (pre-existing match):** The grep pattern `self.*optim` matches an existing line in `skills/eval-rubric/rubrics/eval-harness.md` ("Self-optimization pathway exists."). Running the verify command against the current codebase returns count >= 1, so this criterion passes without any new ACI optimization content being written. Fix: either raise the threshold to >= 2 or narrow the search path to exclude rubric files (e.g., restrict to `skills/*/SKILL.md` instead of `skills/`).

### Weight Verification

| Criteria | Weights |
|----------|---------|
| 1-6 (deterministic) | 7 + 5 + 7 + 7 + 5 + 4 = 35% |
| 7-12 (LLM-as-judge) | 12 + 12 + 10 + 8 + 13 + 10 = 65% |
| **Total** | **100%** |

Weights sum correctly to 100%.

### Testability Assessment

- **Criteria 1-3, 5-6:** Deterministic, file-existence and grep checks. Testable and discriminating.
- **Criterion 4:** Deterministic but currently a no-op (see Issue 7 above). Needs fix before approval.
- **Criteria 7-12:** LLM-as-judge with multi-part PASS requirements. Each sub-criterion is specific and verifiable. Reference solutions provided for 7, 8, 9, and 11 give the grader concrete anchors.
- **SN1-SN2:** Both verifiable via grep. SN1 threshold is meaningful. SN2 checks for calibration example preservation.

### Approved Criteria

Criteria 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, SN1, SN2 — **approved**.

Criterion 4 — **not approved** pending fix for pre-existing match (Issue 7).
