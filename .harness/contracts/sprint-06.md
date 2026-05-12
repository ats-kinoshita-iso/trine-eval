# Sprint 06 Contract: JIT Context Retrieval Patterns

## What I Will Build

Document just-in-time (JIT) context retrieval patterns across all agent and skill files: each step specifies the minimal set of files to read at that point rather than listing all available files up front. Sub-agent spawns in the workflow skill provide a condensed context summary instead of instructing the sub-agent to read the full file set independently. Files document which reads can be deferred until actually needed (lazy loading).

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `deterministic` (code-verifiable) or `llm-judge` (requires reading comprehension).
Weights must sum to 100% across all success criteria.

### Deterministic (code-verifiable)

1. **Generator documents JIT context retrieval** [weight: 8%]: `agents/generator.md` contains explicit JIT or on-demand context retrieval guidance (terms like "jit", "just-in-time", "on-demand", "pull context", "context retrieval", or "read only what"). Verify: `grep -ci 'jit\|just.in.time\|on.demand\|pull.*context\|context.*retrieval\|read only what\|only.*necessary' plugins/trine-eval/agents/generator.md` >= 2.

2. **Sprint-workflow documents per-step context scoping** [weight: 9%]: `skills/sprint-workflow/SKILL.md` contains per-step guidance listing the minimal set of files to read at that step. Verify: `grep -ci 'minimal.*set\|only.*necessary\|context.*scope\|per.step.*context\|deferred\|lazy\|pull.*context\|context.*retrieval' plugins/trine-eval/skills/sprint-workflow/SKILL.md` >= 3.

3. **Sprint-workflow documents condensed sub-agent context** [weight: 9%]: `skills/sprint-workflow/SKILL.md` documents that sub-agent spawns include a condensed context summary rather than pointing to the full file set. Verify: `grep -ci 'condensed\|context.*summary\|summary.*context\|context.*snapshot\|inline.*context\|compact.*context' plugins/trine-eval/skills/sprint-workflow/SKILL.md` >= 2.

4. **Harness-kickoff documents per-step context scoping** [weight: 6%]: `skills/harness-kickoff/SKILL.md` documents which files are read at each step and why, not "read everything at the start." Verify: `grep -ci 'minimal.*set\|only.*necessary\|context.*scope\|deferred\|lazy\|pull.*context\|context.*retrieval' plugins/trine-eval/skills/harness-kickoff/SKILL.md` >= 2.

5. **Evaluator documents JIT context retrieval** [weight: 5%]: `agents/evaluator.md` contains guidance that context is pulled on-demand per evaluation step rather than front-loaded. Verify: `grep -ci 'jit\|just.in.time\|on.demand\|pull.*context\|context.*retrieval\|read only what\|only.*necessary\|minimal.*set\|deferred\|lazy' plugins/trine-eval/agents/evaluator.md` >= 2.

6. **At least 4 skill/agent files document lazy-loading** [weight: 5%]: The word "lazy" or "deferred" (in the sense of deferring reads until needed) appears in at least 4 distinct files among the agent and skill files. Verify: `grep -rl 'lazy\|deferred.*read\|read.*defer\|defer.*until\|until.*needed' plugins/trine-eval/agents/ plugins/trine-eval/skills/` | wc -l` >= 4.

### LLM-as-judge (requires reading comprehension)

7. **Per-step context scoping is actionable in sprint-workflow** [weight: 14%]: The sprint-workflow skill must explicitly enumerate, for each of its numbered steps (Step 0 through Step 5), which specific `.harness/` files are read at that step and must NOT instruct sub-agents to read the entire file set at session start. PASS requires: (a) at least 4 of the 6 steps have an explicit "reads: [file list]" annotation or equivalent scoping note, (b) the file lists differ between steps (not the same list repeated), and (c) there is no instruction to "read all harness files" or equivalent front-loading directive.

8. **Sub-agent spawns include condensed context in sprint-workflow** [weight: 14%]: When spawning Generator or Evaluator sub-agents, the sprint-workflow skill must provide condensed inline context rather than only listing file paths for the sub-agent to read independently. PASS requires: (a) at least one Generator spawn and at least one Evaluator spawn include inline context (key facts, current sprint state, or relevant summary — not just a file path list), (b) the condensed context is distinct from the file list (i.e., adds information not deducible from file names alone), and (c) the workflow explicitly notes that condensed context reduces sub-agent cold-start overhead.

9. **Generator agent documents JIT patterns clearly** [weight: 10%]: The generator agent's JIT context guidance must explain: (a) which files to read in CONTRACT_PROPOSAL mode vs. IMPLEMENTATION mode (these should be different lists), (b) that reading is deferred to the step that needs it rather than front-loaded at session start, and (c) at least one example of a read that can be deferred (e.g., "read prior eval results only if this is a retry round"). PASS requires all three elements.

10. **Lazy-loading guidance is explicit and actionable** [weight: 10%]: At least one file must contain a dedicated section or clearly labeled guidance on lazy loading — specifying which reads are deferrable, under what conditions to defer them, and what the cost of eager vs. lazy loading is (in terms of context window usage or session length). PASS requires all three elements: (a) list of deferrable reads, (b) conditions for deferral, and (c) cost/benefit framing.

11. **Context Engineering rubric dimension reaches 5/5** [weight: 10%]: The eval-harness rubric's Context Engineering dimension requires all five elements at 5/5: structured JSON state, prose/data format distinction, compaction guidance, sub-agent isolation with condensed summaries, and JIT context retrieval patterns documented. After this sprint's implementation, reading `plugins/trine-eval/skills/eval-rubric/rubrics/eval-harness.md` and all modified agent/skill files together, an evaluator must be able to confirm all five elements are present across the harness. PASS requires all five elements verifiable by reading the files.

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT remove compaction guidance from generator**: The generator agent's compaction survival guidance from Sprint 4 must remain intact. Verify: `grep -ci 'compact\|context.*limit\|context.*window\|persist.*state' plugins/trine-eval/agents/generator.md` >= 2.

2. **Should NOT remove compaction guidance from evaluator**: The evaluator agent's context management section from Sprint 4 must remain. Verify: `grep -c 'Context Management' plugins/trine-eval/agents/evaluator.md` >= 1.

3. **Should NOT remove session resumption from sprint-workflow**: The existing Session Resumption section must remain. Verify: `grep -c 'Session Resumption' plugins/trine-eval/skills/sprint-workflow/SKILL.md` >= 1.

4. **Should NOT add front-loading directives**: No modified file should instruct an agent to read all available harness files at session start before doing anything else. Verify by reading comprehension: check that no new "read all files" or "read everything in .harness/" instruction appears in any modified file. (LLM-judge gate: grader reads modified files and checks for front-loading instructions — PASS when absent.)

## Reference Solutions

**Criterion 7 — Per-step context scoping in sprint-workflow:**
```markdown
## Step 0: Determine Which Sprint to Run
<!-- Context reads at this step: sprint-state.json (machine state), sprints.json (sprint list) -->
<!-- Deferred: contracts/, evals/ — not needed until Step 1+ -->

1. Read `.harness/sprint-state.json` — current sprint and status only
2. Read `.harness/sprints.json` — sprint list to find next incomplete sprint
(Do NOT read spec.md, contracts, or eval results at this step — those are only needed later)

## Step 1: Contract Negotiation
<!-- Context reads at this step: spec.md, sprints.json, prior contracts/, prior evals/ -->
<!-- Deferred: config.json, progress.md for Step 0 already resolved sprint number -->

### 1a. Generator Proposes Contract
Spawn the Generator subagent with condensed context:
- **Current sprint:** Sprint 3 — "Metrics, saturation, and summary upgrades"
- **Prior sprint outcomes:** Sprint 1 PASS (13/13), Sprint 2 PASS (9/9)
- **Key constraint:** Weights must sum to 100%
- Tell it to read `.harness/spec.md` for full product vision
- Tell it to read `.harness/contracts/sprint-01.md` and `sprint-02.md` for contract examples
(Do NOT tell it to read all files in .harness/ — it reads only what it needs for contract proposal)
```

**Criterion 8 — Condensed sub-agent context in spawn instructions:**
```markdown
### 1b. Evaluator Reviews Contract
Spawn the Evaluator subagent with this condensed context:
- **Task:** Review draft contract for Sprint 3 at `.harness/contracts/sprint-03.md`
- **Sprint context:** Metrics sprint — adds pass@k, pass^k, saturation graduation to eval-summary
- **Prior evaluation baseline:** Sprint 1 and 2 are approved and passing; don't re-evaluate them
- **What to read:** Only the draft contract at the path above — not the full .harness/ directory
- Append feedback to the contract file under `## Evaluator Review`
<!-- Condensed context above replaces: "read spec.md, read all prior contracts, read all evals" -->
<!-- Sub-agent gets what it needs to act, not a list of files to discover context from -->
```

**Criterion 10 — Lazy-loading guidance:**
```markdown
## Lazy Loading: Deferrable Context Reads

The following reads can be deferred until the step that actually needs them:

| Read | Default timing | Deferral condition | Deferred until |
|------|---------------|-------------------|----------------|
| Prior sprint contracts | Step 0 | Only needed for contract proposal | Step 1a |
| Prior eval results | Step 1a | Only needed if this is a retry round | Step 4 (retry) |
| Full spec.md | Step 0 | Generator already knows sprint title from sprints.json | Step 1a when writing contract |
| Rubric file | Step 3a | Not needed until evaluation begins | Step 3b |
| progress.md | Step 0 | Only needed if sprint-state.json is absent | Fallback only |

**Cost of eager loading:** Reading all harness files at session start consumes 3,000-8,000 tokens
of context window before the agent has done any useful work. In long sessions with many sprints,
this front-loading accelerates context compaction and may cause earlier information loss.

**Lazy loading rule:** Read a file at the step where its contents first influence a decision.
```

## Out of Scope

- Changes to the eval-harness rubric content (rubric scores are evaluated, not modified by this sprint)
- New skills or agents — this sprint modifies existing files only
- Changes to hooks or config schema (completed in Sprint 4)
- Bootstrap workflow changes (completed in Sprint 5)
- Runtime enforcement of JIT patterns (the harness is documentation-only; agents read docs to behave correctly)

## Technical Notes

- This sprint is documentation-only: all deliverables are additions or edits to existing markdown files
- The five Context Engineering rubric requirements were: (1) structured JSON state — Sprint 4, (2) prose/data format distinction — Sprint 4, (3) compaction guidance — Sprint 4, (4) sub-agent isolation with condensed summaries — this sprint, (5) JIT patterns documented — this sprint
- "Condensed context" for sub-agent spawns means inline facts and state the sub-agent needs, not a full file listing. The distinction: "read .harness/spec.md, .harness/sprints.json, all prior contracts" is a file list; "Sprint 3 of 6, prior sprints 1-2 passed, building metrics sprint" is condensed context
- Lazy loading applies to context reads within agent instructions, not to any runtime code
- Per-step context scoping in sprint-workflow means each numbered Step section documents its own minimal read set, not a global "reads at start of session" list
- Criterion 6's verification command has a shell pipe: the evaluator should run it in bash as written, counting unique file paths returned by grep -rl

## Evaluator Review

**Status: APPROVED**

### Baseline Verification (all deterministic criteria)

| # | Criterion | Current baseline | Required | Verdict |
|---|-----------|-----------------|----------|---------|
| 1 | Generator JIT terms | 0 | >= 2 | Zero baseline — discriminating |
| 2 | Workflow per-step scoping | 0 | >= 3 | Zero baseline — discriminating |
| 3 | Workflow condensed context | 0 | >= 2 | Zero baseline — discriminating |
| 4 | Kickoff per-step scoping | 0 | >= 2 | Zero baseline — discriminating |
| 5 | Evaluator JIT terms | 0 | >= 2 | Zero baseline — discriminating |
| 6 | Lazy-loading breadth (4+ files) | 0 | >= 4 | Zero baseline — discriminating |

No no-ops found. All six deterministic criteria require new content.

### Should-NOT Gate Baselines

| # | Gate | Current baseline | Required | Verdict |
|---|------|-----------------|----------|---------|
| SN1 | Generator compaction guidance | 4 | >= 2 | Baseline positive — regression buffer of 2 |
| SN2 | Evaluator Context Management section | 1 | >= 1 | Baseline positive — no regression buffer |
| SN3 | Session Resumption section | 1 | >= 1 | Baseline positive — no regression buffer |
| SN4 | No front-loading directives | N/A (llm-judge) | absence check | Valid gate |

### Weight Verification

| Category | Criteria | Weights |
|----------|----------|---------|
| Deterministic | C1-C6 | 8 + 9 + 9 + 6 + 5 + 5 = 42% |
| LLM-as-judge | C7-C11 | 14 + 14 + 10 + 10 + 10 = 58% |
| **Total** | | **100%** |

Weights sum correctly.

### Feature Coverage

| Feature | Criteria covering it |
|---------|---------------------|
| jit-context-retrieval-documentation | C1, C5, C9 |
| per-step-context-scoping | C2, C4, C7 |
| sub-agent-condensed-summaries | C3, C8 |
| lazy-loading-guidance | C6, C10 |

All four sprint features covered by at least two criteria each.

### Criterion-by-Criterion Assessment

**C1 (8%, deterministic):** 7 grep alternatives, threshold >= 2. A meaningful JIT section produces 2+ matching lines. Testable.

**C2 (9%, deterministic):** 8 patterns, threshold >= 3. Workflow has 6 steps, so 3 matches ensures scoping spans multiple steps. Good.

**C3 (9%, deterministic):** Tests "condensed" terminology specifically. Threshold >= 2 ensures the concept appears in multiple spawn instructions. Clean.

**C4 (6%, deterministic):** Same family as C2 but for kickoff. Lower weight reflects fewer steps in kickoff. Appropriate.

**C5 (5%, deterministic):** Broadest pattern (10 alternatives), lowest threshold (>= 2). Evaluator is a secondary target. Appropriate weight.

**C6 (5%, deterministic):** Breadth check — 4+ files with lazy-loading terms. Prevents single-file concentration. Good. Minor formatting note: stray backtick in the inline verification command.

**C7 (14%, llm-judge):** Three-part requirement: (a) 4+ steps annotated, (b) lists differ between steps, (c) no front-loading. Part (b) prevents copy-paste of the same list. Reference solution provided. Approved.

**C8 (14%, llm-judge):** Tests condensed context in sub-agent spawns. Part (c) requiring explicit cold-start overhead note ensures "why" is documented, not just "what." Reference solution provided. Approved.

**C9 (10%, llm-judge):** Distinguishes contract-proposal reads from implementation reads. The terms "CONTRACT_PROPOSAL mode" and "IMPLEMENTATION mode" are conceptual — grader should accept equivalent phrasing. No reference solution needed given specific sub-requirements. Approved.

**C10 (10%, llm-judge):** Lazy-loading with three elements: deferrable reads, conditions, cost/benefit. Part (c) forces articulation of why lazy loading matters. Reference solution with table format provided. Approved.

**C11 (10%, llm-judge):** Meta-criterion: all five Context Engineering rubric elements present. Four of five from Sprint 4; this validates Sprint 6 adds the final two without regressing. Approved.

**SN4 (llm-judge gate):** Complements C7(c) — both check front-loading absence, but SN4 covers all modified files while C7(c) targets sprint-workflow only. Overlap acceptable since SN4 is a gate. Approved.

### Reference Solutions

Provided for C7, C8, C10 — the three criteria where "file path list" vs "condensed context" distinction is subtlest. C9 and C11 lack references but have sufficiently specific sub-requirements. Adequate.

### Minor Notes (non-blocking)

1. C6 formatting: stray backtick in the verification command markdown. Evaluator can parse the intent.
2. SN1 regression buffer: baseline 4, threshold 2. Could lose 2 lines and still pass. Low risk since sprint adds content.
3. C9 terminology: "CONTRACT_PROPOSAL mode" / "IMPLEMENTATION mode" are labels, not required text. Grader should accept equivalent phrasing.

### Approved Criteria

All 11 success criteria (C1-C11) and all 4 Should-NOT criteria (SN1-SN4) are **approved**.
