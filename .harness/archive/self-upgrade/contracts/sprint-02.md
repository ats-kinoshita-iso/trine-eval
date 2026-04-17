# Sprint 02 Contract: Evaluator Separation and Isolation

## What I Will Build

Upgrade the evaluator to score each rubric dimension in a separate reasoning pass (isolated per-dimension judging), add explicit environment isolation guidance for clean-state between eval trials, and enhance the evaluator's calibration system with project-specific extension points.

## Success Criteria

### Deterministic (code-verifiable)

1. **Evaluator has per-dimension isolation instructions** [weight: 15%]: `agents/evaluator.md` contains instructions to score each rubric dimension in a separate pass, not all at once. Verify: `grep -c 'separate.*pass\|isolated.*dimension\|one dimension at a time\|each dimension independently' agents/evaluator.md` >= 1.

2. **Evaluator has environment isolation section** [weight: 10%]: `agents/evaluator.md` contains a section about clean-state requirements between eval trials. Verify: `grep -ci 'clean.*state\|fresh.*environment\|isolation\|reset.*between' agents/evaluator.md` >= 2 (at least two references — section header + instructions).

3. **Sprint-workflow has isolation step** [weight: 10%]: `skills/sprint-workflow/SKILL.md` includes instructions for resetting or verifying clean state before each evaluation round. Verify: `grep -ci 'clean.*state\|reset\|fresh\|isolation' skills/sprint-workflow/SKILL.md` >= 1.

4. **Evaluator output template has per-dimension sections** [weight: 10%]: The eval report template in `agents/evaluator.md` structures rubric scores so each dimension has its own assessment block with independently cited evidence. Verify: `grep -c 'Dimension Name\|dimension' agents/evaluator.md` >= 1 (the output template already has this but we verify it remains).

5. **Calibration extension point exists** [weight: 8%]: `agents/evaluator.md` documents how to add project-specific calibration examples beyond the three built-in ones. Verify: `grep -ci 'project-specific\|custom.*example\|additional.*calibration\|extend.*calibration' agents/evaluator.md` >= 1.

### LLM-as-judge (requires reading comprehension)

6. **Per-dimension isolation is actionable** [weight: 15%]: The evaluator instructions explain WHY scoring should be isolated per dimension (prevents halo effect, ensures each dimension is graded on its own evidence) and HOW to do it (assess one dimension, write its score and evidence, then move to the next without revising previous scores). PASS requires both WHY and HOW. [weight: 15%]

7. **Environment isolation covers the right concerns** [weight: 12%]: The isolation guidance addresses at minimum: (a) leftover files from prior trials, (b) cached or stale state, and (c) the evaluator's forked context as the primary isolation mechanism. PASS requires all three concerns addressed. [weight: 12%]

8. **Sprint-workflow isolation is properly sequenced** [weight: 10%]: The workflow skill's isolation step occurs BEFORE spawning the evaluator, not after. The step is positioned in Step 3 (Evaluation) before the evaluator spawn. [weight: 10%]

9. **Calibration extension mechanism is practical** [weight: 10%]: The extension point explains where to place additional examples (file path or section), what format they should follow, and that they should cover the project's specific failure modes. PASS requires all three. [weight: 10%]

## Should-NOT Criteria

1. **Should NOT reduce evaluator's adversarial stance**: The evaluator's opening instructions about being skeptical and resisting the bias to rationalize away failures must remain intact. Verify: `grep -c 'BREAK the application\|Resist this' agents/evaluator.md` >= 2.

2. **Should NOT remove forked context**: The evaluator's `context: fork` frontmatter field must remain. Verify: `grep -c 'context: fork' agents/evaluator.md` >= 1.

## Reference Solutions

**Criterion 6 — Per-dimension isolation instructions:**
```markdown
## Per-Dimension Scoring

Score each rubric dimension in a separate pass. Do not score all dimensions at once.

**Why:** Scoring multiple dimensions simultaneously creates a halo effect — a strong impression on one dimension (e.g., functionality works perfectly) biases scoring on other dimensions (e.g., code quality gets inflated). Isolated scoring forces you to evaluate each dimension on its own evidence.

**How:** For each dimension in the rubric:
1. Read the dimension's scoring criteria
2. Gather evidence specific to that dimension only
3. Assign a score with cited evidence
4. Move to the next dimension without revising previous scores
```

**Criterion 7 — Environment isolation guidance:**
```markdown
## Environment Isolation

Each evaluation trial must start from a known, clean state. Shared state between runs can artificially inflate or deflate scores.

Before each evaluation:
- Verify no leftover artifacts from prior trials (temporary files, test databases, cached responses)
- The evaluator runs in a forked context (`context: fork`), providing context isolation from the generator
- If the sprint involves running servers or services, verify they start fresh rather than reusing prior state
```

## Out of Scope

- Pass@k and pass^k metrics (Sprint 3)
- Structured JSON state tracking (Sprint 4)
- Hooks expansion (Sprint 4)
- Changes to the planner agent
- Changes to the generator agent

## Technical Notes

- The evaluator already has `context: fork` for context isolation — this sprint adds guidance for artifact/state isolation
- Per-dimension scoring changes the evaluator's process but not its output format (rubric scores section already exists)
- The calibration extension point should be additive — existing examples must not be removed (gate SN1 from Sprint 1 established this precedent)

## Evaluator Review

**Status: APPROVED**

### Weight Validation

Weights sum to 100%: 15 + 10 + 10 + 10 + 8 + 15 + 12 + 10 + 10 = 100. Confirmed correct.

### Feedback

**Criterion 1 (15%, deterministic) — Per-dimension isolation instructions:**
- Testability: Good. The grep pattern covers reasonable phrasings. However, the alternation `separate.*pass` could false-positive on unrelated uses of "pass" (e.g., "separate pass/fail" in a different context). Acceptable risk given the file is narrowly scoped.
- Specificity: Clear pass/fail boundary (count >= 1). Two evaluators would agree.
- No changes needed.

**Criterion 2 (10%, deterministic) — Environment isolation section:**
- Testability: Good. The threshold of >= 2 matches is a reasonable proxy for "section header + body content."
- Specificity: The word "isolation" in the grep pattern could match pre-existing text. The evaluator already contains "context isolation" at line 61 of the reference solution template and potentially in the current file. This means the criterion could pass before any work is done if the existing file already contains >= 2 matches. However, the existing evaluator.md contains only one match for "isolation" (in a Technical Notes reference, not the evaluator itself — it appears only in forked-context descriptions). Marginal risk but acceptable.
- No changes needed.

**Criterion 3 (10%, deterministic) — Sprint-workflow isolation step:**
- Testability: The grep pattern includes "reset" which is broad. The existing SKILL.md already contains the word "reset" at line 123 ("Resume from the appropriate step" is not a match, but "Check git log" / session resumption context could match on other content). Let me verify: the current file does not contain "reset" as a standalone match. Acceptable.
- Specificity: Clear threshold (>= 1). Adequate.
- No changes needed.

**Criterion 4 (10%, deterministic) — Per-dimension output template:**
- Testability: Weak. The grep for `Dimension Name|dimension` has a low bar — the existing evaluator.md already contains `{Dimension Name}` at line 112 and the word "dimension" appears in multiple places. This criterion is essentially testing that existing content is not removed, which the contract acknowledges ("already has this but we verify it remains"). As a regression guard, this is fine, but 10% weight is high for a no-op verification.
- Specificity: Adequate — two evaluators would agree, since it is just checking existing content persists.
- Recommendation: Weight is generous for a regression check. Not blocking, but noted.

**Criterion 5 (8%, deterministic) — Calibration extension point:**
- Testability: Good. The grep pattern targets distinctive phrases that would only appear in new extension-point documentation.
- Specificity: Clear threshold. Adequate.
- No changes needed.

**Criterion 6 (15%, llm-judge) — Per-dimension isolation is actionable:**
- Testability: Good for LLM-as-judge. The PASS gate is explicit: requires BOTH a WHY explanation (halo effect, own evidence) AND a HOW procedure (sequential assessment without revision). Two sub-requirements, both clearly stated.
- Specificity: The reference solution provides a concrete calibration target. Two evaluators should agree on presence/absence of WHY and HOW.
- Reference solution: Directly useful — it models the exact structure expected.
- No changes needed.

**Criterion 7 (12%, llm-judge) — Environment isolation concerns:**
- Testability: Good. Three required sub-points are explicitly enumerated: (a) leftover files, (b) cached/stale state, (c) forked context. PASS requires all three.
- Specificity: The checklist structure makes agreement straightforward.
- Reference solution: Useful — maps directly to the three required concerns.
- Minor observation: Concern (c) "forked context as the primary isolation mechanism" is already present in the existing evaluator. The criterion tests that the new isolation section explicitly frames it alongside artifact concerns, which is a valid integration requirement.
- No changes needed.

**Criterion 8 (10%, llm-judge) — Workflow isolation sequencing:**
- Testability: Adequate. Requires reading the workflow file and verifying step ordering. An LLM-as-judge criterion is appropriate here since ordering is structural, not easily captured by grep.
- Specificity: "BEFORE spawning the evaluator" and "positioned in Step 3 before the evaluator spawn" are unambiguous positional requirements. Two evaluators would agree.
- No reference solution provided. This is acceptable because the criterion is about placement within an existing file structure, not about content generation.
- No changes needed.

**Criterion 9 (10%, llm-judge) — Calibration extension is practical:**
- Testability: Good. Three explicit sub-requirements: (a) where to place examples, (b) what format, (c) coverage of project-specific failure modes. PASS requires all three.
- Specificity: Clear checklist. Two evaluators would agree.
- No reference solution provided. A reference solution would strengthen this criterion since "practical" is subjective, but the three sub-requirements sufficiently constrain the judgment. Acceptable.
- No changes needed.

### Should-NOT Criteria Assessment

**SN1 — Adversarial stance preserved:**
- Reasonable and well-constructed. The grep targets two specific, distinctive phrases ("BREAK the application" and "Resist this") that exist at lines 11 and 13 of the current evaluator. This is a proper regression gate. The threshold of >= 2 requires both phrases to survive.

**SN2 — Forked context preserved:**
- Reasonable. The `context: fork` frontmatter field is the foundational isolation mechanism. Removing it would silently break evaluator independence. Good gate.

Both Should-NOT criteria are deterministic, verifiable, and target genuinely critical invariants.

### Reference Solutions Assessment

Two reference solutions are provided, both for LLM-as-judge criteria (6 and 7). These are the two highest-weighted LLM-judge criteria (15% and 12%), which is the right prioritization. The solutions are concrete, correctly structured, and match the criterion requirements point-for-point. No reference solution is provided for criteria 8 or 9, which is acceptable given their lower weight and more constrained pass conditions.

### Missing Criteria

1. **No criterion tests that existing calibration examples are preserved.** The Technical Notes state "existing examples must not be removed" and reference Sprint 1's SN1 gate, but there is no corresponding Should-NOT criterion in this contract. This is a real gap: the generator could accidentally delete the three calibration examples while adding the extension point. Recommendation: add a Should-NOT criterion equivalent to Sprint 1's SN1 (`grep -c 'Example:' agents/evaluator.md >= 3`). Severity: moderate — the risk is real but partially mitigated by SN1 only checking two phrases, not the full calibration section.

2. **No criterion tests that per-dimension scoring integrates with the existing evaluation process.** Criteria 1 and 6 verify the instructions exist and are actionable, but neither verifies that the existing "Your process" section (lines 64-76 of evaluator.md) is updated to reference per-dimension scoring during the rubric scores step. The generator could add a standalone section that is never referenced in the actual evaluation workflow. Severity: low — an LLM following the evaluator instructions would likely find the new section regardless of cross-references, but explicit integration would be stronger.

3. **No criterion validates the weight proportionality of this contract's own criteria.** Criterion 4 carries 10% for verifying existing content persists (a regression check), while Criterion 6 carries 15% for entirely new instructional content. The relative weights are defensible but not tested by any criterion. This is a meta-observation, not a blocking gap.

### Approved Criteria

Criteria 1, 2, 3, 5, 6, 7, 8, 9 — well-formed, testable, and specific.

Criterion 4 — approved with the note that 10% weight is generous for a regression-only check. Not blocking.

All Should-NOT criteria approved.
