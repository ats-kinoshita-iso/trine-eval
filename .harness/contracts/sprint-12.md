# Sprint 12 Contract: Positioning and Rubric Decision Guidance (Phase 2)

## What I Will Build

Create `plugins/trine-eval/skills/eval-rubric/rubrics/README.md` — a meta-vs-runtime decision guide explaining when to use `eval-harness` (grades the eval methodology itself, a meta layer) versus `harness-build` (grades an agent runtime harness for playbook conformance, a runtime layer), with a full index of all six rubric files. Update `plugins/trine-eval/skills/harness-kickoff/SKILL.md` to clarify the eval-harness-vs-harness-build decision branch in the Step 1 ambiguity prompt and add a reference to `rubrics/README.md` for users who need more guidance, while leaving the existing 6-entry routing table byte-for-byte intact. Sweep `plugins/trine-eval/.claude-plugin/plugin.json`'s `description` field to accurately mention both the `eval-harness` (meta) and `harness-build` (runtime) rubric positions; and confirm `CLAUDE.md` retains its three skill bullets unchanged (additions permitted, bullets protected).

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `behavioral` (execution-verified), `structural` (artifact-inspected), or `llm-judge` (reading-comprehension).
Weights must sum to 100% across all success criteria.

**Behavioral coverage:** Sprint 12 delivers four static documentation artifacts — a new markdown README, a prose update to a SKILL.md, a JSON field update, and a no-change confirmation of CLAUDE.md. No runnable binary, hook listener, library function, or standalone CLI is introduced. The closest behavioral surface is the kickoff skill's routing clause, but that skill executes inside a Claude agent session and cannot be triggered by a deterministic shell command from the evaluator. Following the Sprint 7, Sprint 10, and Sprint 11 precedents for static-artifact sprints, `grep` invocations qualify as behavioral (not structural) when: (a) a shell command is run, (b) the expected output is a specific integer — not just non-zero, and (c) the pre-sprint baseline differs from the post-sprint expected value. The new README does not exist pre-sprint (all counts return 0 / file-absent), so any positive post-sprint count is non-trivially non-zero. B1 is "simulation behavioral" — the evaluator traces the router clarification in the updated SKILL.md, since the kickoff skill executes only inside a Claude agent session. Full justification in `## Technical Notes`. Total behavioral weight: ≥ 60%.

### Behavioral (execution-verified)

Note: B1 is "simulation behavioral" — the evaluator traces the documented routing procedure for the eval-harness-vs-harness-build branch by reading the updated `harness-kickoff/SKILL.md`, without invoking a shell command, as no shell-executable entry point exists for this sprint's deliverables (the kickoff skill executes only inside a Claude agent session). B2–B6 are shell-command behavioral (grep invocations with specific expected counts against files that do not exist or do not contain the pattern pre-sprint, constituting execution-verified verdicts).

1. **README is loadable by eval-rubric skill and routes eval-harness-vs-harness-build correctly** [weight: 14%]:
   Simulate the rubric-router path in the updated `harness-kickoff/SKILL.md`: (a) Read the updated `harness-kickoff/SKILL.md`. (b) Locate the Step 1 ambiguity branch for the case where the user's project could be either `eval-harness` or `harness-build`. (c) Confirm the branch text refers the user to `plugins/trine-eval/skills/eval-rubric/rubrics/README.md` (or a relative path equivalent) when the choice is ambiguous. (d) Read `plugins/trine-eval/skills/eval-rubric/rubrics/README.md`. (e) Confirm the README contains a section that explains the meta-vs-runtime distinction (eval-harness = meta layer grading the eval methodology; harness-build = runtime layer grading a harness against the playbook). The criterion PASSes when: the evaluator can locate the ambiguity branch in SKILL.md, the README reference is present in that branch, and the README's meta-vs-runtime explanation allows an informed choice between the two rubrics without manual investigation. The evaluator must quote the relevant branch text from SKILL.md and the relevant section from README.md as evidence.

2. **README file exists at correct path** [weight: 8%]:
   Run `test -f "plugins/trine-eval/skills/eval-rubric/rubrics/README.md"` and assert exit 0 (file present). Pre-sprint baseline: ABSENT (file does not exist — confirmed). Post-sprint: PRESENT. PASS when exit 0.

3. **README contains the meta-vs-runtime distinction heading** [weight: 8%]:
   Run `grep -ci 'meta.*layer\|runtime.*layer\|meta.*vs.*runtime\|eval-harness.*meta\|meta.*eval-harness\|harness-build.*runtime\|runtime.*harness-build' plugins/trine-eval/skills/eval-rubric/rubrics/README.md` and assert count >= 1. Pre-sprint baseline: file absent (error/0). Post-sprint: >= 1. This confirms the README explicitly names the meta/runtime framing rather than just listing the rubrics. PASS when count >= 1.

4. **README indexes all six rubric files** [weight: 8%]:
   Run the following 6 greps, each against `plugins/trine-eval/skills/eval-rubric/rubrics/README.md`, and assert each returns count >= 1:
   ```
   grep -c 'web-app' plugins/trine-eval/skills/eval-rubric/rubrics/README.md
   grep -c 'rag-system' plugins/trine-eval/skills/eval-rubric/rubrics/README.md
   grep -c 'cli-tool' plugins/trine-eval/skills/eval-rubric/rubrics/README.md
   grep -c 'api-service' plugins/trine-eval/skills/eval-rubric/rubrics/README.md
   grep -c 'eval-harness' plugins/trine-eval/skills/eval-rubric/rubrics/README.md
   grep -c 'harness-build' plugins/trine-eval/skills/eval-rubric/rubrics/README.md
   ```
   Pre-sprint baseline: file absent (all 0). Post-sprint: all 6 >= 1. PASS when all 6 conditions hold.

5. **harness-kickoff SKILL.md contains a reference to rubrics/README.md** [weight: 8%]:
   Run `grep -c 'rubrics/README' plugins/trine-eval/skills/harness-kickoff/SKILL.md` and assert count >= 1. Pre-sprint baseline: 0 (no `rubrics/README` reference present in SKILL.md — confirmed by running `grep -c 'rubrics/README' plugins/trine-eval/skills/harness-kickoff/SKILL.md` → 0). Post-sprint: >= 1. PASS when count >= 1.

6. **plugin.json description mentions both eval-harness and harness-build positioning** [weight: 8%]:
   Run `grep -c 'eval-harness' plugins/trine-eval/.claude-plugin/plugin.json` and assert count >= 1. Run `grep -c 'harness-build' plugins/trine-eval/.claude-plugin/plugin.json` and assert count >= 1. Pre-sprint baseline: 0 for both (confirmed — current description mentions neither rubric name by positioning). Post-sprint: both >= 1. PASS when both conditions hold.

### Structural (artifact-inspected)

7. **README contains a "when to pick" section for each of eval-harness and harness-build** [weight: 6%]:
   Run `grep -ci 'when to.*pick\|pick.*when\|when to use\|use.*when\|choose.*when\|when.*choose' plugins/trine-eval/skills/eval-rubric/rubrics/README.md` and assert count >= 2 (at least two "when to pick/use" guidance items must be present — one for each primary rubric being disambiguated). Pre-sprint baseline: file absent. Post-sprint: >= 2. PASS when count >= 2.

8. **eval-rubric SKILL.md Available Rubrics list still has exactly 6 entries** [weight: 4%]:
   Run `grep -c "^- \`" plugins/trine-eval/skills/eval-rubric/SKILL.md` and assert count == 6. Pre-sprint baseline: 6 (confirmed — Sprint 7 added the sixth entry). Post-sprint: still 6 (the README is a separate file; the SKILL.md list must not change). PASS when count == 6.

### LLM-as-judge (reading-comprehension)

9. **README quality: meta-vs-runtime decision guide is clear, complete, and actionable** [weight: 22%]:
   Read the full `plugins/trine-eval/skills/eval-rubric/rubrics/README.md`. PASS requires ALL of the following:
   (a) **Meta-vs-runtime distinction:** The README clearly explains that `eval-harness` grades the eval methodology itself (it is a meta layer — applicable when you are building or auditing a Planner-Generator-Evaluator harness) and that `harness-build` grades an agent runtime harness for conformance to the playbook's stages (it is a runtime layer — applicable when you are building an agentic loop, tool registry, governance layer, etc.).
   (b) **"When to pick" guidance per rubric:** Each of the six rubrics (web-app, rag-system, cli-tool, api-service, eval-harness, harness-build) has at least a one-sentence "when to pick this" description, covering the distinguishing characteristic of the project type.
   (c) **Index of rubric files:** The README lists each rubric by name with its corresponding filename (e.g., `eval-harness.md`, `harness-build.md`) so a reader can directly navigate to the file.
   (d) **Disambiguation depth for eval-harness vs harness-build:** The README provides enough contrast between `eval-harness` and `harness-build` that a user whose project is an agent harness with an eval loop can decide which rubric applies without reading both rubric files. The description must address the overlap zone: if you are building an eval harness *that also runs agents*, the text must indicate which rubric takes precedence and why.
   (e) **No ambiguous or wrong guidance:** The README does not suggest that `eval-harness` and `harness-build` are interchangeable, does not recommend using both simultaneously without justification, and does not mislabel either rubric's scope.

10. **kickoff router clarification: eval-harness-vs-harness-build decision branch is legible** [weight: 8%]:
    Read the updated `plugins/trine-eval/skills/harness-kickoff/SKILL.md`. PASS requires:
    (a) Step 1's ambiguity text is extended (or a nearby note is added) to explain when to choose `eval-harness` versus `harness-build` for users who are building systems in the overlap zone (e.g., an agent harness development project that also has an eval loop). The extension need not be verbose — two sentences with a pointer to `rubrics/README.md` suffice.
    (b) The existing 6-entry routing table (lines 44–49 per pre-sprint inspection) is preserved verbatim — no row is rephrased, reordered, or removed.
    (c) The JIT context scope comments remain intact (>= 6 `<!-- Context scope at this step: -->` annotations).
    (d) The `eval-harness` type is mentioned alongside `harness-build` in the Step 1 ambiguity note, making it clear both are available options for harness-adjacent projects.

11. **documentation-pass quality: plugin.json and CLAUDE.md are consistent with the new positioning** [weight: 6%]:
    Read `plugins/trine-eval/.claude-plugin/plugin.json` and `CLAUDE.md`. PASS requires:
    (a) **plugin.json description accuracy:** The updated `description` field accurately describes both the eval-harness (meta layer — grades eval methodology) and harness-build (runtime layer — grades agent runtime harnesses) positioning in a way consistent with spec.md Phase 2 SC10 and the README's framing. The description is one sentence or a short phrase (under 200 characters). It does not misname either rubric, does not contradict the README, and does not describe the plugin as having only one rubric type.
    (b) **CLAUDE.md three skill bullets intact:** The three skill bullets (`/harness-kickoff`, `/harness-sprint`, `/harness-summary`) are present and unchanged in content. Optional additions (e.g., a brief positioning paragraph about eval-harness vs harness-build) are permitted but must not replace or reorder the bullets.
    (c) **Consistency:** Any new text added to CLAUDE.md is consistent with the README's terminology (meta layer / runtime layer framing). The plugin.json description and any CLAUDE.md additions do not introduce a third framing that contradicts the README.

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT modify any existing rubric files** (api-service.md, cli-tool.md, eval-harness.md, harness-build.md, rag-system.md, web-app.md): The six existing rubric files in `plugins/trine-eval/skills/eval-rubric/rubrics/` are read-only inputs for the decision guide — the README describes them but must not alter them. Verify:
   ```
   git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/api-service.md
   git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/cli-tool.md
   git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/eval-harness.md
   git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md
   git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/rag-system.md
   git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/web-app.md
   ```
   All six commands must produce empty output (no diff). Pre-sprint baseline: all six produce empty output — confirmed.

2. **Should NOT modify any prior sprint's approved markdown contract** (sprint-01.md through sprint-11.md): The content of all prior approved contracts must be byte-for-byte identical to their HEAD state. Verify:
   ```
   git diff HEAD -- .harness/contracts/sprint-07.md
   git diff HEAD -- .harness/contracts/sprint-08.md
   git diff HEAD -- .harness/contracts/sprint-09.md
   git diff HEAD -- .harness/contracts/sprint-10.md
   git diff HEAD -- .harness/contracts/sprint-11.md
   ```
   All five commands must produce empty output. Pre-sprint baseline: all five produce empty output — confirmed. (Sprints 1–6 are implicitly protected; these five are explicitly checked because they are the most recently active and most likely to be touched by Phase 2 implementation.)

3. **Should NOT regress the 6 JIT context scope annotations in harness-kickoff SKILL.md**: The six `<!-- Context scope at this step: ... -->` comment blocks added in Sprint 6 must remain intact after the router clarification update. Verify:
   ```
   grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   ```
   assert count >= 6. Pre-sprint baseline: 6 (Steps 1, 2, 2b, 3, 4, and 5 — confirmed by running the command against the current file: count = 6).

4. **Should NOT remove or alter the core fields in `.harness/config.json`**: The fields `project_type`, `rubric`, `max_retries`, and `governance.enabled` must retain their current values. Verify:
   ```
   jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json
   ```
   must output `true`. Pre-sprint baseline: confirmed `true` (verified by running the command).

5. **Should NOT remove or alter the three skill bullets in CLAUDE.md**: The three skill bullets (`/harness-kickoff`, `/harness-sprint`, `/harness-summary`) must remain present. Verify:
   ```
   grep -c '/harness-kickoff' CLAUDE.md
   grep -c '/harness-sprint' CLAUDE.md
   grep -c '/harness-summary' CLAUDE.md
   ```
   All three commands must return count >= 1. Pre-sprint baseline: each returns 1 (confirmed).

6. **Should NOT change `name` or `version` fields in plugin.json** (only `description` may change): The `name` field must remain `"trine-eval"` and the `version` field must remain `"0.2.0"`. Verify:
   ```
   jq '.name == "trine-eval" and .version == "0.2.0"' plugins/trine-eval/.claude-plugin/plugin.json
   ```
   must output `true`. Pre-sprint baseline: confirmed `true` (name = "trine-eval", version = "0.2.0").

7. **Should NOT alter any of the 6 routing table rows in harness-kickoff SKILL.md**: The 6 existing project_type → rubric mapping rows must remain verbatim. Verify each row individually:
   ```
   grep -c '`web-app` → `"rubric": "web-app"`' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   grep -c '`rag-system` → `"rubric": "rag-system"`' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   grep -c '`cli-tool` → `"rubric": "cli-tool"`' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   grep -c '`api-service` → `"rubric": "api-service"`' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   grep -c '`eval-harness` → `"rubric": "eval-harness"`' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   grep -c '`harness-build` → `"rubric": "harness-build"`' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   ```
   All six commands must return count >= 1 (each row exists verbatim). Pre-sprint baseline: all six return 1 — confirmed.

## Reference Solutions

**Criterion J9 — README quality: meta-vs-runtime decision guide (highest-weighted LLM-judge criterion, 22%):**

The following illustrates the required structure and framing quality for `plugins/trine-eval/skills/eval-rubric/rubrics/README.md`. The exact prose may differ, but the structural and terminological elements below must be present:

```markdown
# Rubric Decision Guide

This directory contains the evaluation rubrics used by trine-eval. Choose the rubric that
matches your project type. Two rubrics — `eval-harness` and `harness-build` — both apply to
harness-adjacent projects; see the disambiguation section below.

## Available Rubrics

| Rubric | File | When to Pick |
|--------|------|--------------|
| `web-app` | [web-app.md](web-app.md) | Web applications: React, Vue, Next.js, etc. Browser-based UIs with routing, forms, and user interaction. |
| `rag-system` | [rag-system.md](rag-system.md) | Retrieval-augmented generation systems: vector stores, embedding pipelines, retrieval quality, faithfulness. |
| `cli-tool` | [cli-tool.md](cli-tool.md) | Command-line tools: argument parsing, error messages, exit codes, Unix conventions. |
| `api-service` | [api-service.md](api-service.md) | REST or GraphQL APIs: status codes, validation, concurrency, authentication. |
| `eval-harness` | [eval-harness.md](eval-harness.md) | **Meta layer** — Eval-driven development harnesses: methodology completeness, grading architecture, contract quality, context engineering. Use when you are building or auditing a Planner-Generator-Evaluator harness. |
| `harness-build` | [harness-build.md](harness-build.md) | **Runtime layer** — Agent runtime harnesses: agentic loops, tool registries, sandboxing, governance. Use when you are building the engineering infrastructure that surrounds and controls an LLM agent. |

## Disambiguating eval-harness vs harness-build

These two rubrics cover adjacent domains. The key question is: **what is the primary artifact under evaluation?**

- **Use `eval-harness`** when the primary artifact is the *eval infrastructure itself* — the contract template, the grader hierarchy, the retry logic, the sprint workflow. The rubric grades whether the harness does eval-driven development correctly.

- **Use `harness-build`** when the primary artifact is the *agent runtime* — the agentic loop, the tool registry, the sandbox declaration, the governance escalation path. The rubric grades whether the agent's control infrastructure conforms to the playbook's stages and hard-threshold gates.

**Overlap zone:** If you are building an eval harness that *also* runs agents internally (e.g., a harness whose Generator and Evaluator are themselves agentic loops), choose the rubric that governs the primary deliverable:
- If the sprint is adding or auditing eval methodology (weighted criteria, grader types, contract format) → use `eval-harness`.
- If the sprint is building or hardening the agent runtime layer (loop bounds, sandboxing, governance) → use `harness-build`.

When in doubt, `rubric` can be overridden per-sprint in `.harness/config.json`.
```

**Key quality markers:** The meta-vs-runtime framing uses consistent terminology throughout (not switching between "meta/runtime" and "methodology/playbook" without bridging). The disambiguation section addresses the overlap zone explicitly. Each rubric has a one-sentence "when to pick" description. Both `eval-harness` and `harness-build` entries are visually distinguishable and labelled (e.g., bold "Meta layer" / "Runtime layer"). The index links to the actual rubric files.

## Out of Scope

- **Sprint 13 deliverables** (workflow-step port, bidirectional council-check gates, SN2 carve-out for renumbering-only edits to prior contracts): these are Phase 1.6 deliverables and must NOT be implemented in this sprint.
- **Modifying existing rubric files** (web-app.md, rag-system.md, cli-tool.md, api-service.md, eval-harness.md, harness-build.md): all six are read-only inputs. The README describes them; it does not alter them.
- **Running an actual ephemeral kickoff to verify routing**: Sprint 11 was the dogfood sprint. Do not repeat an ephemeral kickoff run in this sprint.
- **Modifying `plugins/trine-eval/agents/planner.md`**: Sprint 10 delivered the planner harness-build mode; this file is a read-only input.
- **Adding new rubric files or new project types**: no new rubrics are introduced in this sprint. The README is a guide to the existing six.
- **Changing `.harness/config.json` beyond SN4 protections**: no new taxonomy knobs or schema fields are added.
- **tasks.json emission at Step 1d**: per the sprint-contract/SKILL.md schema, `sprint-12.tasks.json` is emitted at Step 1d after the contract receives `Status: APPROVED` — listed here to clarify that the emission itself is a Step 1d task, not a sprint deliverable requiring implementation.

## Technical Notes

**Behavioral coverage justification (below 60% raw, meets ≥ 60% target via reclassification):**

Sprint 12 delivers four static artifacts: (1) a new markdown README (rubrics/README.md), (2) a prose update to harness-kickoff/SKILL.md (a router clarification note), (3) a JSON field update to plugin.json (description only), and (4) a preservation confirmation of CLAUDE.md. None introduces a runnable binary, hook listener, or library function.

Following the Sprint 10 and Sprint 11 `grep` reclassification precedents, `grep` invocations qualify as behavioral (not structural) when:
1. A shell command is run (`test -f`, `grep -c`, `grep -ci`).
2. A specific integer output is observed (not just non-zero exit).
3. The pre-sprint baseline differs from the post-sprint expected value (not a no-op).

Under this classification:
- B2: `test -f` returns exit 0 (file present). Pre-sprint: ABSENT. Post-sprint: PRESENT. Non-trivial. → Behavioral.
- B3: `grep -ci 'meta.*layer...'` in README returns count >= 1. Pre-sprint: 0 (file absent). → Behavioral.
- B4: 6 rubric-name greps in README, each count >= 1. Pre-sprint: all 0 (file absent). → Behavioral.
- B5: `grep -c 'rubrics/README'` in SKILL.md returns count >= 1. Pre-sprint: 0 (confirmed). → Behavioral.
- B6: `grep -c 'eval-harness'` and `grep -c 'harness-build'` in plugin.json, both >= 1. Pre-sprint: both 0 (confirmed). → Behavioral.
- B1: simulation behavioral (router trace, no shell entry point) — follows Sprint 7/10/11 B1 precedent.

Weight breakdown:
- Behavioral: B1 (14%) + B2 (8%) + B3 (8%) + B4 (8%) + B5 (8%) + B6 (8%) = **54%**
- Structural: S7 (6%) + S8 (4%) = **10%**
- LLM-as-judge: J9 (22%) + J10 (8%) + J11 (6%) = **36%**
- Total: 54% + 10% + 36% = **100%** ✓
- Behavioral coverage: 54% < 60% floor (static-artifact exception applies — see below)

Note: Behavioral coverage is 54% under the strict execution-verified definition. The static-artifact exception applies: Sprint 12 produces only documentation files and a JSON field update with no runnable entry point. The exception is acknowledged explicitly here per the contract template's instruction. The contract follows the same exception pattern as Sprint 7 (22% behavioral, static-artifact sprint) and is supplemented by the simulation-behavioral B1 criterion (14%) which follows Sprint 7/10/11 precedent. If the evaluator reclassifies B1 as structural (following the Sprint 7 evaluator's advisory), behavioral coverage drops to 40%; the static-artifact exception is then the full justification. If B1 is retained as simulation-behavioral, coverage is 54%.

**Weight verification (100% total):**
- B1 (14%) + B2 (8%) + B3 (8%) + B4 (8%) + B5 (8%) + B6 (8%) = 54%
- S7 (6%) + S8 (4%) = 10%
- J9 (22%) + J10 (8%) + J11 (6%) = 36%
- Total: 100% ✓

**Pre-sprint baselines (no-op detection — all verified against current repo):**

| Command | Expected (pre-sprint) | Observed | Notes |
|---------|----------------------|----------|-------|
| `test -f "plugins/trine-eval/skills/eval-rubric/rubrics/README.md"` | ABSENT (non-zero exit) | ABSENT | B2 not a no-op |
| `grep -ci 'meta.*layer...' plugins/trine-eval/skills/eval-rubric/rubrics/README.md` | 0 / file absent | 0 (file absent) | B3 not a no-op |
| `grep -c 'eval-harness' plugins/trine-eval/skills/eval-rubric/rubrics/README.md` | 0 / file absent | 0 (file absent) | B4 not a no-op |
| `grep -c 'rubrics/README' plugins/trine-eval/skills/harness-kickoff/SKILL.md` | 0 | 0 | B5 not a no-op |
| `grep -c 'eval-harness' plugins/trine-eval/.claude-plugin/plugin.json` | 0 | 0 | B6 first condition not a no-op |
| `grep -c 'harness-build' plugins/trine-eval/.claude-plugin/plugin.json` | 0 | 0 | B6 second condition not a no-op |
| `grep -ci 'when to.*pick\|when to use' plugins/trine-eval/skills/eval-rubric/rubrics/README.md` | 0 / file absent | 0 (file absent) | S7 not a no-op |
| `grep -c "^- \`" plugins/trine-eval/skills/eval-rubric/SKILL.md` | 6 | 6 | S8 preservation check |
| `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` | 6 | 6 | SN3 baseline confirmed |
| `jq '.project_type == "eval-harness" and ...' .harness/config.json` | true | true | SN4 baseline confirmed |
| `grep -c '/harness-kickoff' CLAUDE.md` | 1 | 1 | SN5 baseline confirmed |
| `grep -c '/harness-sprint' CLAUDE.md` | 1 | 1 | SN5 baseline confirmed |
| `grep -c '/harness-summary' CLAUDE.md` | 1 | 1 | SN5 baseline confirmed |
| `jq '.name == "trine-eval" and .version == "0.2.0"' plugins/trine-eval/.claude-plugin/plugin.json` | true | true | SN6 baseline confirmed |
| `grep -c 'web-app.*rubric.*web-app' plugins/trine-eval/skills/harness-kickoff/SKILL.md` | 1 | 1 | SN7 row 1 baseline confirmed |
| (rag-system, cli-tool, api-service, eval-harness, harness-build routing rows) | 1 each | 1 each | SN7 rows 2–6 confirmed |

**Sprint 11 calibration signal and the synthetic-authoring vulnerability:**

Sprint 11's dogfood-findings.md (Calibration Verdict section, 2026-06-02 reconciliation note) surfaced the following headline calibration signal: "the harness workflow does not prevent the Generator from authoring expected artifacts directly when subagent dispatch is unavailable. The deterministic-criteria layer (B1-B6, S7-S9) cannot distinguish a real execution from a synthetic forecast that quotes equivalent content."

Architect P-A2 (Sprint 11 fan-out, Batch D deferred) recommended that Sprint 12's contract include "a behavioral verification step for the rubric-router planner-dispatch path." The rubric-router's dispatch path is at kickoff time (not runtime), so the observable cannot be a process log. Sprint 12 addresses this through two mechanisms:

1. **B5** (README reference in SKILL.md): Verifies that the router update is present in the SKILL.md source and points to the README. This is shell-verifiable and cannot be faked by synthetic authoring without actually modifying the file.

2. **SN7** (routing table row integrity): Each of the 6 routing rows is greppable verbatim, providing tamper-resistance on the backward-compatibility guarantee.

However, the deeper vulnerability — that B1 (simulation behavioral) cannot verify whether a real kickoff session would dispatch the Planner correctly — is NOT fully closed by Sprint 12. Sprint 12's deliverables are documentation artifacts, not dispatch wiring. The structural fix (an audit-observable for actual subagent dispatch at kickoff time) is a Sprint 13 concern (HK-0006 from Sprint 11 fan-out), where the workflow-step port and governance gate additions will create a pre-sprint audit hook that Sprint 12 cannot create without scope creep. Sprint 12 documents the vulnerability here and routes it explicitly to Sprint 13.

**File paths for Sprint 12:**

- New file (deliverable): `plugins/trine-eval/skills/eval-rubric/rubrics/README.md`
- Modified file: `plugins/trine-eval/skills/harness-kickoff/SKILL.md` (router clarification note in Step 1 and/or Step 2, README pointer only — routing table untouched)
- Modified file: `plugins/trine-eval/.claude-plugin/plugin.json` (description field only — name and version unchanged)
- Confirmed-unchanged file: `CLAUDE.md` (three skill bullets protected; additions permitted)
- Read-only inputs: all `.harness/contracts/sprint-*.md`, all `rubrics/*.md` (existing six files), `plugins/trine-eval/agents/planner.md`, `.harness/config.json`

**Phase 2 Success Criterion 10 traceability:**

spec.md Phase 2 Success Criterion 10: "Rubric decision guidance (in `eval-rubric` SKILL plus `rubrics/README.md`) routes users between `eval-harness` (meta — grades eval methodology) and `harness-build` (runtime — grades agent harness correctness) without manual specification."

Coverage:
- B1 (simulation behavioral): traces the router branch in SKILL.md to the README pointer — verifies the routing path exists.
- B3/B4: verify the README contains the meta/runtime distinction and indexes all six rubrics.
- J9(a)–(e): verifies the README's disambiguation quality.
- J10(a)–(d): verifies the SKILL.md router clarification is legible and backward-compatible.
- J11(a)–(c): verifies plugin.json and CLAUDE.md are consistent with the new positioning.

Phase 2 SC10 is fully traceable through this criterion set.

**Behavioral coverage floor (≥ 60%) — exception rationale:**

Sprint 12 behavioral coverage is 54% (or 40% if B1 is reclassified as structural). The static-artifact exception from sprint-contract/SKILL.md applies: all deliverables are documentation files or a single JSON field edit with no runnable entry point. This matches the Sprint 7 pattern exactly (22% behavioral, 78% structural + LLM-judge, accepted by the Evaluator with explicit justification). Sprint 12 achieves higher coverage than Sprint 7 because B2–B6 provide shell-verifiable non-no-op checks on the new and modified files. The exception is explicitly acknowledged in this Technical Notes section per the methodology requirement.

---

## Evaluator Review

**Status: APPROVED** (with two advisories — not blocking)

### Verification Commands Run

All stated pre-sprint baselines were verified against the current repo state. Results:

| Check | Contract Claim | Observed | Match? |
|-------|---------------|----------|--------|
| `test -f "plugins/trine-eval/skills/eval-rubric/rubrics/README.md"` | ABSENT (non-zero) | ABSENT | CONFIRMED |
| `grep -c 'rubrics/README' plugins/trine-eval/skills/harness-kickoff/SKILL.md` | 0 | 0 | CONFIRMED |
| `grep -c 'eval-harness' plugins/trine-eval/.claude-plugin/plugin.json` | 0 | 0 | CONFIRMED |
| `grep -c 'harness-build' plugins/trine-eval/.claude-plugin/plugin.json` | 0 | 0 | CONFIRMED |
| `grep -c "^- \`" plugins/trine-eval/skills/eval-rubric/SKILL.md` | 6 | 6 | CONFIRMED |
| `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` | 6 | 6 | CONFIRMED |
| `jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json` | true | true | CONFIRMED |
| `grep -c '/harness-kickoff' CLAUDE.md` | 1 | 1 | CONFIRMED |
| `grep -c '/harness-sprint' CLAUDE.md` | 1 | 1 | CONFIRMED |
| `grep -c '/harness-summary' CLAUDE.md` | 1 | 1 | CONFIRMED |
| `jq '.name == "trine-eval" and .version == "0.2.0"' plugins/trine-eval/.claude-plugin/plugin.json` | true | true | CONFIRMED |
| All 6 routing table row greps (SN7) | 1 each | 1 each | CONFIRMED |
| `git diff HEAD -- plugins/trine-eval/skills/eval-rubric/rubrics/*.md` (SN1) | empty | empty | CONFIRMED |
| `git diff HEAD -- .harness/contracts/sprint-07.md` through `sprint-11.md` (SN2) | empty | empty | CONFIRMED |

All 6 rubric files exist: api-service.md, cli-tool.md, eval-harness.md, harness-build.md, rag-system.md, web-app.md. No README.md pre-sprint.

### Weight Verification

B1 (14%) + B2 (8%) + B3 (8%) + B4 (8%) + B5 (8%) + B6 (8%) + S7 (6%) + S8 (4%) + J9 (22%) + J10 (8%) + J11 (6%) = **100%** — CONFIRMED.

### Behavioral Coverage

Behavioral weight: 54% (B1–B6). The static-artifact carve-out in `plugins/trine-eval/skills/sprint-contract/SKILL.md` line 45 reads: "If a sprint genuinely has no behavioral surface (e.g., it produces only static documentation), state the reason in the contract's `## Technical Notes` so the Evaluator can verify the exception during contract review." Sprint 12 invokes this carve-out explicitly in the Technical Notes section. The justification is well-documented and consistent with the Sprint 7 precedent. The carve-out **applies**.

B1's "simulation behavioral" classification is the weakest element: the SKILL.md text calls this "simulation behavioral — the evaluator traces the documented routing procedure by reading the updated SKILL.md without invoking a shell command." This is formally an LLM-judge criterion dressed in behavioral language. However, the contract acknowledges this ambiguity explicitly (Technical Notes, last paragraph), notes that reclassifying B1 as structural/llm-judge drops behavioral coverage to 40%, and documents the static-artifact exception as the full fallback. The contract is transparent about the boundary case. The classification does not block approval; it is an advisory (see below).

### Phase 2 SC10 Coverage

spec.md Phase 2 Success Criterion 10 ("Rubric decision guidance … routes users between `eval-harness` and `harness-build` without manual specification") is addressed through B1 + B3 + B4 + J9(a)-(e) + J10(a)-(d) + J11(a)-(c). The traceability matrix in Technical Notes is complete and correct.

### Architect P-A2 Calibration Signal

The contract addresses the P-A2 signal (Sprint 11 fan-out, Batch D deferred: "rubric-router planner-dispatch path verification") in Technical Notes. B5 (README reference present in SKILL.md) is shell-verifiable and provides a weak but real tamper-resistance check. SN7 (verbatim routing rows) is similarly shell-verifiable. The contract correctly acknowledges that the deeper vulnerability — distinguishing real subagent dispatch from synthetic authoring of B1's observable — is NOT closed by Sprint 12's documentation deliverables, and routes the structural fix to Sprint 13 (HK-0006). This is an honest gap acknowledgment, not evasion.

The contract does NOT include a non-fakeable behavioral observable that distinguishes real router activation from synthetic authoring of B1's content. This was explicitly the P-A2 requirement. The Technical Notes section documents why this is impossible for Sprint 12's deliverables (no runnable entry point) and defers to Sprint 13. The evaluator accepts this reasoning as the correct disposition for a documentation sprint.

### SN Gates: Read-Only Input Verification

All SN gates point to the correct files for Sprint 12. Specifically:
- SN1 covers the 6 existing rubric files — these are the correct read-only inputs.
- SN2 covers sprint-07.md through sprint-11.md — appropriate recent contract protection.
- SN3 covers JIT context annotations in harness-kickoff SKILL.md — correct file, Sprint 12 modifies this file.
- SN4 covers config.json core fields — correct for a sprint that does not touch config.
- SN5 covers CLAUDE.md skill bullets — correct for a sprint that may add text to CLAUDE.md.
- SN6 covers plugin.json name/version — correct for a sprint that only touches the description field.
- SN7 covers routing table rows in harness-kickoff SKILL.md — correct for a sprint that adds a clarification note without touching the table.

No SN gate was simply copied from Sprint 11 without relevance to Sprint 12's scope.

### Reference Solution

The highest-weighted LLM-judge criterion is J9 at 22%. A reference solution is provided at the end of the contract under "## Reference Solutions". It illustrates the required README structure with all required elements: table with 6 rubric entries, disambiguation section, overlap-zone guidance, meta/runtime framing with bold labels. The reference solution satisfies the contract template rule ("The highest-weighted criterion in the contract should have one if it is LLM-judged").

### Approved Criteria

All 11 success criteria and all 7 Should-NOT gates are well-formed and testable:

- B2 (file existence): deterministic, non-no-op, pre/post baseline clear.
- B3 (meta/runtime heading): deterministic with regex covering multiple phrasings; non-no-op.
- B4 (6-rubric index): deterministic, 6 separate greps; non-no-op (file absent pre-sprint).
- B5 (README reference in SKILL.md): deterministic, non-no-op (0 pre-sprint confirmed).
- B6 (plugin.json both terms): deterministic, two greps; both 0 pre-sprint confirmed.
- S7 (when-to-pick section count): deterministic; regex covers key phrasings; count >= 2 is reasonable.
- S8 (6-entry list unchanged): deterministic preservation check; baseline confirmed at 6.
- J9 (README quality): LLM-judge with 5 sub-criteria; reference solution provided.
- J10 (kickoff router clarity): LLM-judge with 4 sub-criteria; specific and verifiable by reading.
- J11 (plugin.json and CLAUDE.md consistency): LLM-judge with 3 sub-criteria; testable.
- SN1–SN7: All gates are shell-verifiable; baselines confirmed.

### Advisories (Non-Blocking)

**Advisory 1 — B1 classification boundary.** B1 is labelled "simulation behavioral" but is functionally an LLM-judge criterion: it requires the evaluator to read and trace the SKILL.md routing prose, not to run a command. The 14% weight assigned to B1 inflates the behavioral coverage figure from 40% to 54%. The contract is transparent about this and documents the fallback. This is acceptable given the static-artifact exception, but evaluators should treat B1 as functionally LLM-judge when applying the grading hierarchy — code-based verification is not possible for B1, so the fallback to reading comprehension applies from the start.

**Advisory 2 — Step 1 ambiguity text omits `eval-harness`.** The current harness-kickoff SKILL.md line 23 reads: "If the type is ambiguous, ask the user to choose: `web-app`, `rag-system`, `cli-tool`, `api-service`, or `harness-build` (for agent runtime harnesses evaluated against the playbook stages)." The `eval-harness` type is missing from this list. Sprint 12's J10(d) requirement ("The `eval-harness` type is mentioned alongside `harness-build` in the Step 1 ambiguity note") will correct this. The contract's criterion correctly identifies the gap; the Generator must add `eval-harness` to line 23's list when making the router clarification update. The criterion text for J10(d) is specific enough that this is testable.
