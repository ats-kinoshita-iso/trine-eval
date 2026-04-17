# Sprint 03 Contract: Metrics, Saturation, and Summary Upgrades

## What I Will Build

Upgrade the eval-summary skill to compute pass@k and pass^k consistency metrics from retry-round data, identify saturated criteria for regression suite graduation, and add a regression suite recommendation section to the summary output.

## Success Criteria

### Deterministic (code-verifiable)

1. **eval-summary mentions pass@k** [weight: 10%]: `skills/eval-summary/SKILL.md` contains the term "pass@k". Verify: `grep -c 'pass@k' skills/eval-summary/SKILL.md` >= 1.

2. **eval-summary mentions pass^k** [weight: 10%]: `skills/eval-summary/SKILL.md` contains the term "pass^k" or "pass\^k". Verify: `grep -cE 'pass\^k|pass\\\^k' skills/eval-summary/SKILL.md` >= 1.

3. **eval-summary has saturation graduation section** [weight: 8%]: The summary output template in `skills/eval-summary/SKILL.md` includes a "Saturation" or "Regression" section. Verify: `grep -ci 'saturation\|regression suite\|graduation' skills/eval-summary/SKILL.md` >= 2 (at least in computation instructions AND output template).

4. **eval-summary output template includes consistency metrics** [weight: 8%]: The summary output format in `skills/eval-summary/SKILL.md` includes fields for pass@k and pass^k values. Verify: `grep -cE 'pass@k|pass\^k|consistency' skills/eval-summary/SKILL.md` >= 2 (at least in computation AND output sections).

5. **eval-summary defines computation formulas** [weight: 8%]: `skills/eval-summary/SKILL.md` includes the mathematical definitions. Verify: `grep -ci 'probability\|formula\|1.*-.*1.*-.*p\|p.*\^.*k\|at least one' skills/eval-summary/SKILL.md` >= 1.

### LLM-as-judge (requires reading comprehension)

6. **pass@k definition is correct** [weight: 12%]: `skills/eval-summary/SKILL.md` defines pass@k as the probability of at least one success in k attempts: `pass@k = 1 - (1-p)^k` where p is the per-trial pass rate. The definition must be mathematically correct and explained clearly enough for an LLM to compute it from eval data.

7. **pass^k definition is correct** [weight: 12%]: `skills/eval-summary/SKILL.md` defines pass^k as the probability all k trials succeed: `pass^k = p^k` where p is the per-trial pass rate. The definition must distinguish this from pass@k and explain when each metric is relevant (pass@k for tools where one success matters, pass^k for customer-facing agents where consistency is essential).

8. **Saturation graduation criteria are actionable** [weight: 15%]: The summary skill defines what makes a criterion "saturated" (e.g., passes on first attempt across N consecutive sprints), what action to take (flag for graduation to regression suite), and how to distinguish criteria that are easy from those that are well-implemented. PASS requires all three elements.

9. **Summary output integrates new metrics naturally** [weight: 17%]: The summary output template places pass@k/pass^k in a logical location (near retry efficiency data), saturation recommendations near the existing recommendations section, and the new sections do not disrupt the existing output structure (Overview, Per-Sprint Results, Trend Analysis, Failure Patterns, Recommendations).

## Should-NOT Criteria

1. **Should NOT remove existing computation sections**: The existing "What to Compute" subsections (Pass Rate, Trend Analysis, Failure Patterns, Retry Efficiency, Saturated Criteria, Recommendations) must all remain. Verify: `grep -c 'Pass Rate\|Trend Analysis\|Failure Patterns\|Retry Efficiency\|Recommendations' skills/eval-summary/SKILL.md` >= 5.

2. **Should NOT remove existing output template sections**: The markdown output template must retain Overview, Per-Sprint Results, Trend Analysis, Common Failure Patterns, and Recommendations. Verify: `grep -c 'Overview\|Per-Sprint Results\|Trend Analysis\|Failure Patterns\|Recommendations' skills/eval-summary/SKILL.md` >= 5.

## Reference Solutions

**Criterion 6 — pass@k definition:**
```markdown
### Consistency Metrics

**pass@k** — The probability of at least one success in k attempts:
`pass@k = 1 - (1 - p)^k`
where p is the per-trial pass rate (passed criteria / total criteria for a single evaluation round).

Use pass@k when one success is sufficient — e.g., a code generation tool where the user picks the best output from multiple runs.
```

**Criterion 7 — pass^k definition:**
```markdown
**pass^k** — The probability that all k trials succeed:
`pass^k = p^k`

Use pass^k when consistency is essential — e.g., a customer-facing agent where every interaction must succeed. At a 75% per-trial pass rate, pass^3 drops to ~42%.
```

**Criterion 8 — Saturation graduation:**
```markdown
### Saturation & Regression Graduation

A criterion is **saturated** when it passes on the first evaluation round across 3+ consecutive sprints. Saturated criteria track regressions but provide no improvement signal.

**Action:** Flag saturated criteria for graduation to a regression test suite. Replace with harder variants that push the agent's capabilities.

**Distinguishing easy from well-implemented:** A criterion that is inherently trivial (e.g., "file exists") saturates because it is easy. A criterion that was previously hard but now consistently passes saturates because the implementation improved. Check the criterion's history: if it ever failed in prior sprints, it represents genuine capability growth. If it has never failed, it may be too easy.
```

## Out of Scope

- Changes to the evaluator agent (completed in Sprints 1-2)
- Changes to the contract template (completed in Sprint 1)
- Changes to hooks or progress format (Sprint 4)
- Actual computation of metrics (this sprint defines the instructions; the summary skill executes them at report time)

## Technical Notes

- The eval-summary skill is instruction-only (no executable code) — it tells the LLM what to compute when invoked
- pass@k and pass^k are computed from retry-round data in `.harness/evals/sprint-NN-rR.md` files
- The existing "Saturated Criteria" subsection in the skill is a starting point but lacks graduation actions and easy/improved distinction
- Per-trial pass rate p = (passed criteria / total criteria) from a single round's eval report

## Evaluator Review

**Status:** APPROVED WITH NOTES

### Feedback

**Weights:** Sum to 100% (10+10+8+8+8+12+12+15+17). Correct.

**Deterministic criteria (1-5) — testability:**

- Criteria 1-2 are clean grep checks. Testable as written.
- Criterion 3: The grep pattern `saturation\|regression suite\|graduation` with threshold >= 2 is reasonable but fragile. The word "graduation" could match in unrelated contexts (e.g., "graduation from Sprint 1 patterns"). Acceptable risk given the file is short and focused, but a tighter pattern like `Regression.*Graduation\|Saturation.*Graduation` would be more precise. Minor concern, not blocking.
- Criterion 4: The grep `pass@k|pass\^k|consistency` with threshold >= 2 could false-positive on the word "consistency" appearing in unrelated prose. However, requiring >= 2 matches across computation AND output sections is a reasonable structural check. Acceptable.
- Criterion 5: The grep pattern `probability\|formula\|1.*-.*1.*-.*p\|p.*\^.*k\|at least one` is extremely broad. The word "probability" alone would satisfy this, even in a sentence like "there is some probability of failure." The criterion says "includes the mathematical definitions" but the grep only proves a keyword exists, not a formula. However, LLM-judge criterion 6 covers the actual correctness of the formula, so this deterministic check serves as a lightweight pre-filter. Acceptable as a complement to criterion 6.

**LLM-judge criteria (6-9) — specificity and completeness:**

- Criterion 6: Well-specified. Includes the exact formula (`pass@k = 1 - (1-p)^k`), defines variables, and requires clarity sufficient for LLM computation. Reference solution provided and matches. Strong.
- Criterion 7: Well-specified. Clearly distinguishes pass^k from pass@k, includes formula (`pass^k = p^k`), and requires explanation of when each is relevant. Reference solution includes a concrete numeric example (75% rate, pass^3 = 42%). Strong.
- Criterion 8: Requires three specific sub-elements (definition of saturated, action to take, easy vs well-implemented distinction). The reference solution is thorough. One minor gap: the criterion says "e.g., passes on first attempt across N consecutive sprints" but the reference solution hardcodes "3+ consecutive sprints." The evaluator will need to judge whether the builder's chosen threshold is reasonable, not just whether it matches the reference exactly. This is fine for LLM-judge grading.
- Criterion 9: Highest weight at 17%. Requires integration "near retry efficiency data" and "near the existing recommendations section" and must not disrupt five named existing sections. This is specific enough to grade but gives the builder reasonable flexibility on exact placement. Good balance.

**Should-NOT criteria — baseline verification:**

- SN1: Current file returns 9 matches against `Pass Rate\|Trend Analysis\|Failure Patterns\|Retry Efficiency\|Recommendations`. Threshold is >= 5. Baseline is healthy; the builder would need to delete multiple sections to trigger failure. Sound.
- SN2: Current file returns 8 matches against `Overview\|Per-Sprint Results\|Trend Analysis\|Failure Patterns\|Recommendations`. Threshold is >= 5. Baseline is healthy. Sound.
- Note: Neither SN1 nor SN2 would detect a scenario where the builder preserves the section headers but guts the content beneath them. This is a known limitation of grep-based gates. The LLM-judge criterion 9 partially covers this by requiring the new sections "do not disrupt the existing output structure."

**Reference solutions:**

- All three are provided (criteria 6, 7, 8). They are concrete, contain the exact formulas, and include contextual guidance. No reference solution is provided for criterion 9, which is reasonable since it tests integration/placement rather than factual correctness.

**Cross-sprint consistency:**

- Sprint 1 eval (rubric "Grading Architecture") noted "missing: pass@k and pass^k metrics" as a gap. Sprint 2 eval reiterated this. This contract directly addresses that gap. Good traceability.
- Sprint 2 eval (rubric "Methodology Completeness") noted "saturation graduation is deferred to Sprint 3." This contract delivers on that deferral. Good.
- The existing SKILL.md line 39-40 already has a one-line "Saturated Criteria" subsection. The contract's Technical Notes acknowledge this ("is a starting point but lacks graduation actions and easy/improved distinction"). The builder should extend this, not duplicate it. The contract does not explicitly say "extend the existing subsection" vs "add a new section." Minor ambiguity, but the reference solution and criterion 3's grep for >= 2 matches implicitly require content in multiple places, which guides toward extending.

### Missing Criteria

1. **No deterministic gate for formula correctness.** Criteria 6 and 7 rely entirely on LLM-as-judge to verify that `pass@k = 1 - (1-p)^k` and `pass^k = p^k` are present as written. A simple grep for the literal formula strings (e.g., `1 - (1 - p)^k` or `1 - (1-p)^k`) would add a cheap deterministic backstop. Not blocking, but would strengthen the contract.

2. **No criterion verifying that the "Saturated Criteria" subsection under "What to Compute" is updated (not just the output template).** Criterion 3 checks for >= 2 matches of saturation/regression/graduation keywords, which could be satisfied entirely within the output template section. A criterion explicitly requiring updates to the computation instructions would be more precise. Partially mitigated by criterion 8 (LLM-judge) requiring actionable graduation criteria.

3. **No Should-NOT gate protecting the existing "How to Generate" section (lines 11-16).** If the builder accidentally modifies data-loading instructions, none of the current criteria would catch it. Low risk given the sprint's scope, but worth noting.

### Approved Criteria

All 9 success criteria and 2 Should-NOT criteria are approved for evaluation. The criteria collectively cover the three deliverables (pass@k/pass^k definitions, saturation graduation, output template integration) with appropriate deterministic and LLM-judge grading. Weights are balanced: deterministic checks (44%) handle presence/structure, LLM-judge checks (56%) handle correctness/quality. The higher weight on LLM-judge criteria is appropriate since the core value of this sprint is in the quality of the definitions and integration, not just keyword presence.
