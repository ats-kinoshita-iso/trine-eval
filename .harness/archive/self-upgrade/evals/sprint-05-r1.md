# Sprint 05 Evaluation
**Round:** 1

## Summary
- Total criteria: 12
- Passed: 11
- Failed: 1
- Weighted score: 92% (sum of passed criteria weights)
- Gate criteria: 2 passed / 2 total
- Verdict: PASS

## Criteria Results

### 1. Bootstrap skill exists [weight: 7%]
**Grader:** deterministic
**Result:** PASS
**Evidence:** File exists at `skills/bootstrap-failures/SKILL.md`. Verified via `test -f` returning EXISTS.
**Location:** skills/bootstrap-failures/SKILL.md

### 2. Bootstrap skill has valid frontmatter [weight: 5%]
**Grader:** deterministic
**Result:** PASS
**Evidence:** `head -5 | grep -c '^---'` returned 2 (opening and closing delimiters within the first 5 lines). `grep -c 'name:\|description:\|allowed-tools:'` returned 3, confirming all three required frontmatter fields are present: `name: bootstrap-failures`, `description: Import real failure cases...`, `allowed-tools: Read, Write, Glob, Grep`.
**Location:** skills/bootstrap-failures/SKILL.md:1-4

### 3. Human calibration has a dedicated section [weight: 7%]
**Grader:** deterministic
**Result:** PASS
**Evidence:** `grep -c '## Human Calibration' agents/evaluator.md` returned 1. The section starts at line 192 and contains substantial content (33 lines) covering when to flag, recording overrides, and the feedback loop.
**Location:** agents/evaluator.md:192

### 4. ACI optimization content exists in a skill definition [weight: 7%]
**Grader:** deterministic
**Result:** PASS
**Evidence:** `grep -rci 'tool.*description.*optim\|transcript.*improv\|eval.*transcript.*feedback' skills/*/SKILL.md` returned 1 match in `skills/eval-summary/SKILL.md`. The match is new content in the "ACI Self-Optimization from Eval Transcripts" section (line 133+), not a pre-existing string. Confirmed the contract's Round 2 review Issue 7 was addressed -- the search is scoped to `skills/*/SKILL.md` which excludes the rubric file that was the false-positive source.
**Location:** skills/eval-summary/SKILL.md:133

### 5. Bootstrap skill references failure sources [weight: 5%]
**Grader:** deterministic
**Result:** PASS
**Evidence:** `grep -ci` returned 15 matches for failure source patterns. The skill explicitly names 5 sources: bug reports (line 19), manual test notes (line 20), production incidents (line 21), support tickets (line 22), and code review comments (line 23). Far exceeds the >= 2 threshold.
**Location:** skills/bootstrap-failures/SKILL.md:17-23

### 6. All skills have valid frontmatter [weight: 4%]
**Grader:** deterministic
**Result:** PASS
**Evidence:** `grep -rl '^---' skills/*/SKILL.md | wc -l` returned 6. All six skill directories have YAML frontmatter: bootstrap-failures, eval-rubric, eval-summary, harness-kickoff, sprint-contract, sprint-workflow.

### 7. Bootstrap workflow is complete [weight: 12%]
**Grader:** llm-judge
**Result:** PASS
**Evidence:** All four required elements verified:
- **(a) Sources of real failures (2+):** Lines 17-23 list 5 sources: bug reports, manual test notes, production incidents, support tickets, code review comments. Each includes context on why it is valuable.
- **(b) Conversion to eval tasks with unambiguous success criteria:** Lines 26-56 describe a detailed conversion process. The JSON schema (lines 29-45) includes `success_criteria` and `reference_solution` fields. The conversion guidelines (lines 49-56) explicitly require "unambiguous success criteria" using the same standard as sprint contracts.
- **(c) Target of 20-50 initial tasks:** Line 60 states "Start with 20-50 real failure cases" with attribution to Anthropic's guidance. Includes the warning about 0% pass rates signaling broken tasks.
- **(d) Integration with sprint contract workflow:** Lines 65-96 describe integration at two touchpoints (kickoff and contract negotiation) with a complete data flow diagram showing the path from raw failures through to eval reports.
**Location:** skills/bootstrap-failures/SKILL.md:17-96

### 8. Human calibration is actionable [weight: 12%]
**Grader:** llm-judge
**Result:** PASS
**Evidence:** All three required elements verified:
- **(a) When to flag for human review:** Lines 196-203 list four specific trigger conditions: low-confidence LLM-judge grades, borderline PASS/FAIL cases, first evaluation of a new rubric dimension, and grader disagreement between code-based and LLM checks.
- **(b) Recording human overrides (specific file path and format):** Lines 206-216 specify the file path `.harness/calibration/human-grades.md` and provide an exact markdown format with fields for LLM grade, human grade, agreement status, and reasoning.
- **(c) Feedback loop for improving grader accuracy:** Lines 220-224 describe three mechanisms: (1) disagreements become new calibration examples, (2) systematic disagreements trigger rubric threshold adjustments, (3) inter-annotator agreement checks. Each is concrete and actionable.
**Location:** agents/evaluator.md:192-224

### 9. ACI self-optimization is grounded in eval data [weight: 10%]
**Grader:** llm-judge
**Result:** PASS
**Evidence:** All three required elements verified:
- **(a) Extracting actionable feedback from eval transcripts:** Lines 137-144 of eval-summary SKILL.md describe four specific things to look for: tool calls that failed, criteria where grader type was wrong, evaluator misinterpretations, and recurring failures across sprints.
- **(b) Concrete improvement process:** Lines 148-153 describe a four-step process: locate the relevant description, propose a change following ACI best practices, apply the change, and document the rationale in the summary.
- **(c) Validation against held-out eval cases:** Lines 157-163 describe selecting 2-3 prior sprint evals not used to derive changes, mentally re-evaluating whether the changes help, and checking for regressions. This is concrete, though it relies on mental re-evaluation rather than automated re-running (which is reasonable given this is a markdown-driven harness, not a test framework).
**Location:** skills/eval-summary/SKILL.md:133-163

### 10. Bootstrap integrates with existing harness [weight: 8%]
**Grader:** llm-judge
**Result:** FAIL
**Evidence:** The bootstrap skill itself describes integration thoroughly (lines 65-96): it references `.harness/bootstrap/failure-catalog.json`, describes how kickoff and contract negotiation consume the catalog, and provides a full data flow diagram. However, the integration is **one-directional** -- the bootstrap skill claims the kickoff will read the catalog, but `skills/harness-kickoff/SKILL.md` contains zero references to "bootstrap", "failure-catalog", or any mention of reading a failure catalog. The kickoff skill was NOT updated to actually consume bootstrap artifacts. The sprint-workflow skill similarly has no reference to bootstrap or the failure catalog. The bootstrap skill describes what *should* happen at the other end of the integration, but the receiving skills have no instructions to do it. A kickoff agent following its SKILL.md instructions would ignore the failure catalog entirely. The data flow exists only in the bootstrap skill's documentation, not in the actual workflow skills that would execute it.
**Location:** skills/bootstrap-failures/SKILL.md:65-96 (describes integration), skills/harness-kickoff/SKILL.md (missing any bootstrap reference)

### 11. Methodology coverage reaches 7+ of 8 steps [weight: 13%]
**Grader:** llm-judge
**Result:** PASS
**Evidence:** Verified each of the 8 steps against the reference mapping table:

- **Step 0 (Start early with real failures):** COVERED. `skills/bootstrap-failures/SKILL.md` is entirely dedicated to this. Lines 8-9 explicitly reference Steps 0 and 1 of Anthropic's methodology. The "Sources of Real Failures" section (lines 17-23) provides 5 concrete failure sources with guidance on prioritizing by user impact.

- **Step 1 (Convert manual tests to automated):** COVERED. `skills/bootstrap-failures/SKILL.md` lines 26-56 describe a structured conversion process with a JSON schema for catalog entries, 6 conversion guidelines, and specific instructions for writing unambiguous success criteria with grader type assignment.

- **Step 2 (Unambiguous tasks with reference solutions):** COVERED. `skills/sprint-contract/template.md` includes a Reference Solutions section (lines 30-33) with instructions to provide known-working outputs. The sprint-contract SKILL.md (lines 56-64) explains when and why to include reference solutions, with emphasis on LLM-judge criteria calibration.

- **Step 3 (Balanced positive/negative test sets):** COVERED. `skills/sprint-contract/template.md` lines 21-22 include the Should-NOT criteria section. The sprint-contract SKILL.md lines 47-53 dedicate a full section to negative criteria with usage guidance (regression guards, security invariants, architectural boundaries).

- **Step 4 (Stable eval environment):** COVERED. `agents/evaluator.md` lines 27-34 contain an "Environment Isolation" section with three specific checks: leftover artifacts, cached/stale state, and forked context isolation. The sprint-workflow SKILL.md lines 67-75 add pre-evaluation clean state checks.

- **Step 5 (Grader hierarchy code->LLM->human):** COVERED. `agents/evaluator.md` lines 17-23 define the "Grading Hierarchy" with three tiers: code-based (preferred), LLM-as-judge (when needed), and human calibration (last resort). The enforcement rule on lines 24-25 makes code-first mandatory.

- **Step 6 (Check transcripts):** COVERED. `agents/evaluator.md` lines 226-239 contain a "Transcript Review" section with explicit instructions to review eval transcripts for grader quality. The eval-summary SKILL.md lines 133-163 add ACI self-optimization from transcript analysis.

- **Step 7 (Saturation monitoring):** COVERED. `skills/eval-summary/SKILL.md` lines 66-76 contain a "Saturation & Regression Graduation" section defining saturation (3+ consecutive first-round passes), graduation actions, and distinguishing easy criteria from genuinely improved ones.

**Result: 8/8 steps covered.** Exceeds the 7+ threshold.

### 12. Transcript review mechanism is explicit [weight: 10%]
**Grader:** llm-judge
**Result:** PASS
**Evidence:** `agents/evaluator.md` lines 226-239 contain a dedicated "## Transcript Review" section that explicitly targets grader quality, not just sprint outcomes. Key evidence:
- Line 228: "review the eval transcript for grader quality — not just sprint outcomes" (emphasis in original)
- Line 230: Direct quote from the playbook: "You won't know if your graders are working well unless you read the transcripts and grades from many trials."
- Lines 233-236 specify four quality checks: (1) whether FAIL verdicts cite specific evidence, (2) whether PASS verdicts verify thoroughly vs. accepting surface compliance, (3) whether LLM-judge grades match rubric descriptions, (4) whether a different evaluator would reach the same verdict.
- Line 238: When discrepancies are found, they get flagged and become calibration examples.
This is unambiguously about grader quality assessment, not sprint outcome review.
**Location:** agents/evaluator.md:226-239

## Gate (Should-NOT) Results

### SN1. Should NOT break existing skill structure
**Result:** PASS
**Evidence:** `grep -rl '^---' skills/*/SKILL.md | wc -l` returned 6. All six skill directories (bootstrap-failures, eval-rubric, eval-summary, harness-kickoff, sprint-contract, sprint-workflow) have valid YAML frontmatter. The new bootstrap-failures skill was added without breaking any existing skill.

### SN2. Should NOT remove evaluator calibration examples
**Result:** PASS
**Evidence:** `grep -c 'Example:' agents/evaluator.md` returned 4. The three built-in calibration examples remain intact: "Good FAIL Report" (line 152), "Good PASS Report" (line 158), "BAD Evaluation" (line 164). The fourth match is from the "Adding Project-Specific Calibration Examples" section (line 170). Exceeds the >= 3 threshold.

## Rubric Scores

### Methodology Completeness (30%): 5/5
All 8 steps of Anthropic's eval methodology are now implemented: early bootstrapping from real failures (bootstrap-failures skill), manual-to-automated conversion (bootstrap conversion process), unambiguous tasks with reference solutions (contract template + reference solutions section), balanced positive/negative test sets (Should-NOT criteria), isolated environments (evaluator environment isolation + workflow pre-eval checks), grader hierarchy code-to-LLM-to-human (evaluator grading hierarchy + human calibration), transcript review (evaluator transcript review section + ACI self-optimization), saturation graduation (eval-summary saturation section). No steps missing.

### Grading Architecture (25%): 5/5
Explicit three-tier grader hierarchy (code -> LLM -> human) documented in the evaluator with enforcement rules. Per-dimension scoring with anti-halo-effect isolation. LLM grading uses structured rubrics with thinking-then-scoring. Human calibration pathway exists with recording format, feedback loop, and inter-annotator agreement checks. pass@k and pass^k metrics documented in eval-summary. Escape hatch ("Unable to assess") mentioned in the LLM-as-judge tier description. Calibration examples provided with instructions for adding project-specific ones.

### Generator-Evaluator Separation (20%): 5/5
Evaluator runs in forked context (context: fork in frontmatter). Contract negotiation happens before implementation (sprint-workflow Step 1 before Step 2). Sprint contracts include weighted criteria, negative test cases (Should-NOT), and reference solutions. The evaluator is independently calibratable with three built-in few-shot examples and instructions for adding more. The evaluator has explicit instructions never to access generator reasoning.

### Context Engineering (15%): 4/5
Structured JSON note-taking via sprint-state.json. Progress log distinguishes prose (markdown) from structured data (JSON) with explicit guidance in the evaluator. Compaction guidance present in evaluator (lines 240-248) and session resumption in sprint-workflow. Sub-agent isolation via forked context. Minor gap: no explicit JIT context retrieval patterns documented -- the harness relies on agents reading files at known paths rather than having a formal JIT retrieval mechanism.

### Extensibility & ACI (10%): 5/5
Custom rubrics supported with a clear template (eval-rubric skill with 5 rubrics and "Adding Custom Rubrics" instructions). Hooks cover key lifecycle events (pre-eval clean state check, post-eval summary, sprint completion). Plugin manifest accurate (all 6 skills with valid frontmatter). Tool descriptions follow ACI best practices (bootstrap skill description is 1 sentence/semantic, evaluator is detailed). Self-optimization pathway exists via ACI self-optimization section in eval-summary with transcript analysis, improvement process, and held-out validation.

## Actionable Feedback

### Criterion 10 FAIL — Bootstrap integration is one-directional

The bootstrap-failures skill describes how the kickoff and contract negotiation should consume the failure catalog, but the receiving skills (`harness-kickoff/SKILL.md` and `sprint-workflow/SKILL.md`) were not updated to reference the catalog. This makes the integration aspirational rather than functional.

**Fix:** Add bootstrap catalog consumption to the kickoff skill. In `skills/harness-kickoff/SKILL.md`, after the "Check if config.json exists" step in Step 1 or at the start of Step 3, add instructions like:

```markdown
## Step 2b: Import Bootstrap Failures (if available)

If `.harness/bootstrap/failure-catalog.json` exists:
1. Read the catalog and group failures by rubric dimension
2. Pass the failure patterns to the Planner alongside the user's prompt
3. Instruct the Planner to prioritize sprints that address critical-severity failures
```

Similarly, in `skills/sprint-workflow/SKILL.md` Step 1a, add an instruction for the Generator to read the failure catalog when proposing contracts.

## Human Review Flags

No criteria flagged for human review. All LLM-judge assessments had clear, unambiguous evidence supporting the verdict. The only FAIL (criterion 10) is based on a verifiable absence: grep for "bootstrap" and "failure-catalog" in the kickoff and workflow skills returns zero matches.
