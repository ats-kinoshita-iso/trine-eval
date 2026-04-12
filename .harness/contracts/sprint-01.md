# Sprint 01 Contract: Grading Hierarchy and Contract Structure

## What I Will Build

Upgrade the evaluator agent to enforce Anthropic's code→LLM→human grading hierarchy, enhance the sprint contract template to support weighted criteria with negative test cases and reference solutions, and fix the plugin manifest to reflect the current project name.

## Success Criteria

### Deterministic (code-verifiable)

1. **Plugin manifest name** [weight: 5%]: `plugin.json` field `name` equals `"trine-eval"`. Verify: `jq -r .name .claude-plugin/plugin.json` outputs `trine-eval`.

2. **Plugin manifest description** [weight: 5%]: `plugin.json` field `description` contains `"trine-eval"` (not just `"eval-harness"`). Verify: `jq -r .description .claude-plugin/plugin.json | grep -c 'trine-eval'` returns >= 1.

3. **Contract template has weight annotations** [weight: 8%]: `skills/sprint-contract/template.md` includes a `[weight: N%]` annotation on at least 5 criterion placeholder lines. Verify: `grep -c '\[weight:' skills/sprint-contract/template.md` returns >= 5.

4. **Contract template has negative criteria section** [weight: 8%]: Template includes a `## Should-NOT Criteria` section with at least one placeholder entry. Verify: `grep -c 'Should-NOT' skills/sprint-contract/template.md` returns >= 1.

5. **Contract template has reference solutions section** [weight: 5%]: Template includes a `## Reference Solutions` section. Verify: `grep -c 'Reference Solutions' skills/sprint-contract/template.md` returns >= 1.

6. **Evaluator mentions both grader types** [weight: 8%]: `agents/evaluator.md` contains the phrases "code-based" AND "LLM-as-judge". Verify: `grep -c 'code-based' agents/evaluator.md` >= 1 AND `grep -c 'LLM-as-judge' agents/evaluator.md` >= 1.

7. **Evaluator has grader type tagging** [weight: 8%]: Evaluator instructs tagging each criterion result with its grader type. `agents/evaluator.md` contains both "deterministic" AND "llm-judge". Verify: `grep -c 'deterministic' agents/evaluator.md` >= 1 AND `grep -c 'llm-judge' agents/evaluator.md` >= 1.

### LLM-as-judge (requires reading comprehension)

8. **Grading hierarchy appears as a numbered list** [weight: 13%]: The evaluator instructions present the grading hierarchy as a numbered or ordered list (not unstructured prose) with code-based as item 1, LLM-as-judge as item 2, and human calibration as item 3. The ordering must be conveyed by list numbering, not merely implied by paragraph order.

9. **Contract skill documents weight system completely** [weight: 10%]: `skills/sprint-contract/SKILL.md` explains all three of: (a) how to assign weights to criteria, (b) that success-criteria weights must sum to 100%, and (c) how weights affect the evaluator's final scoring. PASS requires all three sub-points present.

10. **Negative criteria semantics in skill doc** [weight: 8%]: `skills/sprint-contract/SKILL.md` explains that Should-NOT criteria define behaviors that must NOT occur and are graded PASS when the behavior is absent.

11. **Reference solutions documented as optional in skill doc** [weight: 7%]: `skills/sprint-contract/SKILL.md` explains both: (a) reference solutions are optional (not every criterion needs one), and (b) their purpose is calibrating grader accuracy. PASS requires both points.

12. **Template includes weight-sum guidance** [weight: 5%]: The contract template itself (`skills/sprint-contract/template.md`) includes a note or comment that weights must sum to 100%. Verify: `grep -ci '100%\|sum.*weight\|weight.*sum' skills/sprint-contract/template.md` >= 1.

13. **Evaluator hierarchy enforcement at eval time** [weight: 10%]: `agents/evaluator.md` instructs the evaluator to attempt code-based verification first for each criterion, falling back to LLM judgment only when deterministic verification is not possible. This must be an explicit instruction, not merely implied by the hierarchy list.

## Should-NOT Criteria (gates — any failure blocks the sprint)

1. **Evaluator should NOT remove existing calibration examples**: The three calibration examples (Good FAIL, Good PASS, BAD Evaluation) must still be present. Verify: `grep -c 'Example:' agents/evaluator.md` >= 3.

2. **Contract template should NOT break backward compatibility**: The existing sections (What I Will Build, Success Criteria, Out of Scope, Technical Notes) must still be present. Verify: run four separate greps on `skills/sprint-contract/template.md` for each section header; all four must match.

## Reference Solutions

**Criterion 3 — Weight annotation syntax:**
```
1. {Criterion}: {How to verify} [weight: N%]
```

**Criterion 8 — Grading hierarchy as numbered list:**
```markdown
## Grading Hierarchy

1. **Code-based grading** (preferred) — Run deterministic checks first: exact match, regex, exit codes, file existence, JSON schema validation, command output comparison.
2. **LLM-as-judge grading** (when needed) — For subjective or nuanced criteria that cannot be verified by code. Use structured rubrics. Reason in thinking tags before scoring.
3. **Human calibration** (last resort) — Spot-check sampling to validate that code-based and LLM graders agree with expert judgment.
```

**Criterion 13 — Hierarchy enforcement instruction:**
```markdown
For each criterion, attempt deterministic verification first (run a command, check a file, validate output). Only fall back to LLM judgment when the criterion requires subjective assessment that no code check can capture.
```

## Out of Scope

- Changes to eval-summary (Sprint 3)
- Changes to hooks (Sprint 4)
- Changes to progress.md format (Sprint 4)
- Adding new rubric dimensions to existing domain rubrics
- Changes to the planner agent
- Changes to the generator agent beyond ensuring consistency with the updated contract template

## Technical Notes

- All changes are to markdown and JSON files
- The contract template is used by both the sprint-contract skill and the generator agent — both must be consistent
- The evaluator agent currently has `context: fork` which provides separation — do not remove this
- Weight syntax should be parseable by both humans and simple regex for potential future automation
- Should-NOT criteria are gates: they do not carry scoring weight but any failure is an automatic sprint FAIL

## Evaluator Review (Round 2)

**Status: APPROVED**

### Feedback

All six concerns from Round 1 have been addressed:

1. **Weight accounting (fixed):** Should-NOT criteria are now explicitly labeled as gates with no scoring weight. Success criteria weights sum to exactly 100% (5+5+8+8+5+8+8+13+10+8+7+5+10).

2. **Threshold/description alignment (fixed):** All thresholds match their textual descriptions (e.g., Criterion 3 says "at least 5" and verifies >= 5; Should-NOT 1 says "three calibration examples" and verifies >= 3).

3. **File disjunctions resolved (fixed):** Every criterion now targets a single, specific file path. No "or" disjunctions between files remain.

4. **Compound criteria addressed (fixed):** Criteria 9 and 11 now have explicit sub-point lists with "PASS requires all three sub-points present" and "PASS requires both points" respectively. Criteria 6 and 7 use explicit AND conjunctions with separate grep checks for each required phrase.

5. **Missing criteria added (fixed):** Plugin manifest description (Criterion 2), weight-sum guidance in template (Criterion 12), and hierarchy enforcement at eval time (Criterion 13) are all present with clear verification methods.

6. **Reference solutions present (fixed):** Reference solutions exist for the highest-weighted LLM-judge criterion (Criterion 8, 13%) and two others (Criteria 3 and 13), giving the evaluator concrete calibration material.

**Minor note (non-blocking):** Should-NOT 2 describes four section-header greps but does not spell out the exact grep commands, unlike all other deterministic checks. The section names are unambiguous so this is acceptable, but the evaluator will need to construct the commands from the listed names.

### Approved Criteria

- **C1** (Plugin manifest name, 5%, deterministic): Well-formed. Single jq command with exact expected output.
- **C2** (Plugin manifest description, 5%, deterministic): Well-formed. Grep for "trine-eval" in description field.
- **C3** (Contract template weight annotations, 8%, deterministic): Well-formed. Grep count with threshold matching description.
- **C4** (Contract template negative criteria section, 8%, deterministic): Well-formed. Grep for section header.
- **C5** (Contract template reference solutions section, 5%, deterministic): Well-formed. Grep for section header.
- **C6** (Evaluator mentions both grader types, 8%, deterministic): Well-formed. Two independent grep checks joined by AND.
- **C7** (Evaluator has grader type tagging, 8%, deterministic): Well-formed. Two independent grep checks joined by AND.
- **C8** (Grading hierarchy as numbered list, 13%, LLM-judge): Well-formed. Clear rubric (numbered list, specific ordering) with reference solution provided.
- **C9** (Contract skill documents weight system, 10%, LLM-judge): Well-formed. Three explicit sub-points with all-required clause.
- **C10** (Negative criteria semantics, 8%, LLM-judge): Well-formed. Single clear requirement about absence-means-pass semantics.
- **C11** (Reference solutions documented as optional, 7%, LLM-judge): Well-formed. Two explicit sub-points with both-required clause.
- **C12** (Template includes weight-sum guidance, 5%, LLM-judge): Well-formed. Grep provides deterministic floor; LLM-judge classification allows evaluator to confirm semantic adequacy.
- **C13** (Evaluator hierarchy enforcement, 10%, LLM-judge): Well-formed. Clear behavioral requirement (attempt code-based first, fall back to LLM) with reference solution.
- **SN1** (No removal of calibration examples, gate): Well-formed. Grep count >= 3 for "Example:" occurrences.
- **SN2** (No backward-incompatible template changes, gate): Well-formed. Four section headers enumerated by name.
