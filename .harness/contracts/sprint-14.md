# Sprint 14 Contract: Durability & Clean Baseline (P0)

## Revision History

| Rev | Date | Change |
|-----|------|--------|
| 0 | 2026-06-03 | Initial draft (main-thread, minimal mode — Evaluator forked) |

## What I Will Build

Bring the working tree to a clean, durable, **pushed** baseline before any further phase work, without rewriting any prior history. Three deliverables:

(a) **Commit the governance audit trail** — `.council/audit-log.jsonl` has ~964 uncommitted appended lines (the log-tool-call hook's record of the Cycle-3 governance work). Commit it as-is (append-only; never rewrite prior content).

(b) **Prune stale worktree gitlinks** — `git rm` the two stale gitlink entries `.claude/worktrees/focused-hofstadter-3b9fb5` and `.claude/worktrees/jolly-perlman-094dc3` (leftover agent worktrees already deleted on disk, still tracked as gitlinks).

(c) **Reach a clean, committed baseline and push** — commit the remaining intended changes so the working tree carries no uncommitted *non-session* content, then **push** `meta-eval/self-upgrade` (49 local-only commits). The push is a **human-gated irreversible action** surfaced for explicit confirmation at sprint completion — it is NOT a graded criterion.

## Success Criteria

Weights sum to 100% across success criteria. Tagged behavioral / structural / llm-judge.

### Behavioral (execution-verified — run via git-bash)

1. **Audit-log committed and tracked** [weight: 25%]:
   `git ls-files --error-unmatch .council/audit-log.jsonl` exits 0 (tracked), AND the most recent commit touching it is a Sprint-14 commit: `git log --oneline -1 -- .council/audit-log.jsonl` contains `sprint-14` or `sprint 14` (case-insensitive). PASS when both hold.
   Pre-sprint baseline: the file is tracked but has uncommitted appended content (`git status --porcelain .council/audit-log.jsonl` is non-empty → ` M`).

2. **Both stale worktree gitlinks removed** [weight: 25%]:
   `git ls-files .claude/worktrees/focused-hofstadter-3b9fb5 .claude/worktrees/jolly-perlman-094dc3 | wc -l` returns `0`.
   Pre-sprint baseline: both are tracked (the `git status` shows them as ` D` deletions pending staging). PASS when count == 0.

3. **No stale worktree gitlinks remain tracked** [weight: 20%]:
   `git ls-files .claude/worktrees | wc -l` returns `0` (no worktree gitlinks tracked at all).
   Pre-sprint baseline: 2 (the two stale entries). PASS when count == 0.

4. **Working tree carries no uncommitted non-session content at completion** [weight: 15%]:
   At sprint completion (after the Step-5 commit), `git status --porcelain` contains no entries other than (i) `.claude/settings.local.json` (operator-local, git-ignored-by-convention) and (ii) the harness session-state files the Step-5 commit will itself carry (`.harness/progress.md`, `.harness/sprint-state.json`) if evaluated pre-commit. The Evaluator verifies that no *unexpected* file is left dirty/untracked: `git status --porcelain | grep -vE 'settings.local.json|progress.md|sprint-state.json' | wc -l` returns `0`. **Evaluation timing (Evaluator Issue #1):** B4 is graded AFTER the Step-5 commit, which commits the sprint's own artifacts (`sprint-14.md`, `sprint-14.tasks.json`, `evals/sprint-14-r1.md`, `sprint-prebrief/sprint-14.json`); those must be committed (not left `??`) before B4 is graded.

### Structural (artifact-inspected)

5. **Branch is ahead of origin and ready to push (push readiness)** [weight: 15%]:
   `git rev-list --count origin/meta-eval/self-upgrade..HEAD` returns a positive integer (commits exist to push), and `git status -sb` shows the branch tracks `origin/meta-eval/self-upgrade`. This grades *readiness*; the actual push is the human-gate completion action. PASS when the count is ≥ 1 and the upstream is set.

## Should-NOT Criteria (gates)

1. **Should NOT rewrite or truncate `.council/audit-log.jsonl`** (append-only): the committed file's line count must be ≥ its pre-sprint line count. Verify: `git show HEAD:.council/audit-log.jsonl | wc -l` (post-commit) ≥ the pre-sprint working-copy line count (**baseline: working-copy 2347 lines, HEAD-committed 1321 — per Evaluator Issue #2**). No `git rebase`, `git commit --amend` on prior commits, or history rewrite of the audit log.

2. **Should NOT modify any prior sprint's contract, eval, decision, or henkaten record**: `git diff HEAD~N HEAD -- .harness/contracts/sprint-0*.md .harness/contracts/sprint-1[0-3].md .harness/evals/ .council/decision-log.jsonl .council/henka-register.jsonl` (for the sprint's own commits) shows only *appends* to the jsonl logs and no edits to prior contracts/evals. Verify the JIT-annotation regression gate still passes: `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` ≥ 6.

3. **Should NOT force-push or push to any branch other than `meta-eval/self-upgrade`**: the push (when human-confirmed) targets only the current feature branch with a plain `git push` (no `--force`, no `--force-with-lease` unless explicitly requested, no push to `main`).

4. **Should NOT alter `.harness/config.json` core fields**: `jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json` outputs `true`.

## Reference Solutions

**Criterion 1 (audit-log committed) — reference approach:**

```bash
git add .council/audit-log.jsonl
git commit -m "chore(sprint-14): commit governance audit-log trail (P0 durability)"
# verify:
git ls-files --error-unmatch .council/audit-log.jsonl   # exit 0
git log --oneline -1 -- .council/audit-log.jsonl         # shows the sprint-14 commit
```

**Criteria 2/3 (worktree gitlinks) — reference approach:**

```bash
git rm .claude/worktrees/focused-hofstadter-3b9fb5 .claude/worktrees/jolly-perlman-094dc3
# (already deleted on disk; git rm stages the removal)
git commit -m "chore(sprint-14): prune stale worktree gitlinks (P0)"
git ls-files .claude/worktrees | wc -l   # 0
```

## Out of Scope

- **The push is not a graded criterion** — it is a human-gated irreversible completion action (criterion 5 grades *readiness* only).
- **No version bump, marketplace.json, or main-branch merge** — those are Sprint 15 (P1).
- **No regression-pipeline or SKILL edits** — Sprint 16 (P2).
- **No governance-schema work** — Sprint 17 (P3).
- **No rewriting of session-noise semantics** — `progress.md` SESSION_STOPPED markers and the `sprint-state.json` timestamp are hook-generated; they are committed as-is by the normal Step-5 checkpoint, not "cleaned."

## Technical Notes

**Mode:** Sprint 14 runs in effective minimal mode (main-thread implementation; Evaluator forked). Rationale: P0 deliverables are git-state operations plus a human-gated push, which the main thread owns more naturally than a Generator subagent, while the Evaluator's independence (the harness's core invariant) is fully preserved via the forked grading subagent. `config.components_enabled` does not set `generator_subagent: true`, so minimal-mode is config-consistent.

**Grader split:** behavioral 85% (B1 25 + B2 25 + B3 20 + B4 15) / structural 15% (S5) / llm-judge 0%. Behavioral coverage 85% ≥ 60% floor; no carve-out needed. All four behavioral criteria are exit-code-or-count deterministic (the exact polarity discipline Sprint 16/P2 will codify — note that criterion 1/2/3 use `wc -l == 0` / explicit-exit forms with correct polarity).

**Push human-gate:** surfaced at Step 5 completion via council-autorun's reversibility handling (`git push` = irreversible → mandatory confirmation). The sprint PASSES on criteria 1–5 + gates regardless of whether the user confirms the push in this session; an un-pushed-but-ready baseline still satisfies the graded contract (criterion 5 grades readiness). The durability benefit is only realized once the user confirms the push.

**Pre-sprint baselines (verified):** `git status --porcelain .council/audit-log.jsonl` → ` M`; `git ls-files .claude/worktrees | wc -l` → 2; `git rev-list --count origin/meta-eval/self-upgrade..HEAD` → 49.

## Evaluator Review

**Reviewer:** Claude Sonnet 4.6 (forked CONTRACT_REVIEW)
**Date:** 2026-06-03

### Pre-Sprint Baseline Verification

All four baseline commands run cleanly under git-bash and match the contract's claimed values:

| Command | Expected | Actual | Match |
|---------|----------|--------|-------|
| `git status --porcelain .council/audit-log.jsonl` | ` M` | ` M .council/audit-log.jsonl` | YES |
| `git ls-files .claude/worktrees \| wc -l` | `2` | `2` | YES |
| `git rev-list --count origin/meta-eval/self-upgrade..HEAD` | `49` | `49` | YES |
| `git ls-files .claude/worktrees/focused-hofstadter-3b9fb5 .claude/worktrees/jolly-perlman-094dc3 \| wc -l` | `2` | `2` | YES |

### Per-Criterion Testability Verdicts

**B1 (Audit-log committed, 25%):** TESTABLE. Both sub-checks are deterministic. The `git ls-files --error-unmatch` exit-code check is unambiguous. The `git log --oneline -1` grep for `sprint-14`/`sprint 14` (case-insensitive) is sufficient. No quoting issues under git-bash.

**B2 (Both stale gitlinks removed, 25%):** TESTABLE. `git ls-files <path1> <path2> | wc -l` returning `0` is unambiguous. Polarity is correct (0 = PASS). The two paths are exactly as shown by `git status --porcelain` (` D` entries).

**B3 (No worktree gitlinks remain, 20%):** TESTABLE and REDUNDANT-BUT-HARMLESS relative to B2 — B3 is a superset check (`git ls-files .claude/worktrees | wc -l == 0`) that would catch any other undetected worktree gitlinks. Redundancy with B2 is acceptable for a P0 durability sprint; having both at 25%+20% is intentional defense-in-depth.

**B4 (No uncommitted non-session content, 15%):** TESTABLE with one **non-blocking defect** — see Issue #1 below.

**S5 (Push readiness, 15%):** TESTABLE. `git rev-list --count origin/meta-eval/self-upgrade..HEAD` returns 49 (positive), and `git status -sb` confirms `## meta-eval/self-upgrade...origin/meta-eval/self-upgrade [ahead 49]`. This correctly grades readiness, not the push itself. Upstream is already set. PASS condition (count ≥ 1 and upstream set) is unambiguous.

### SN Gate Verification

**SN1 (append-only audit log):** CHECKABLE. Pre-sprint working-copy line count is 2347; HEAD-committed count is 1321. After B1's commit lands, `git show HEAD:.council/audit-log.jsonl | wc -l` will return ~2347 ≥ 2347. The logic is sound. **One procedural note:** the evaluator must capture the pre-sprint working-copy line count BEFORE the sprint runs (i.e., record the 2347 value now), or compare post-sprint HEAD against the working copy if the sprint is evaluated in one session. The contract does not specify how the evaluator captures the pre-sprint working-copy count. This is a mild ambiguity — low-severity because in practice the evaluator runs at a known point in time — flagged as a non-blocking advisory.

**SN2 (no prior artifact rewrite):** CHECKABLE. The `git diff` glob covers `sprint-0*.md` (sprints 01–09) and `sprint-1[0-3].md` (sprints 10–13) — correctly excludes sprint-14.md from the protected set. The JIT-annotation regression gate `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` returns `6` (≥ 6 required) — PASSES now and should be unaffected by sprint-14 deliverables.

**SN3 (no force-push):** CHECKABLE post-hoc by examining the push command used (human-gated; evaluator can inspect the council-autorun output or git reflog).

**SN4 (config core fields):** CHECKABLE. `jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json` returns `true` now and is unaffected by sprint-14 deliverables. Per the contract's own note: jq without `-e` always exits 0 regardless of `true`/`false` output — the evaluator must read stdout ("true"/"false"), not the exit code. The contract correctly documents this workaround.

### Issues Found

**Issue #1 — B4 grep exclusion does not cover untracked sprint-session files (non-blocking, fix recommended):**

The B4 verification command is:
```
git status --porcelain | grep -vE 'settings.local.json|progress.md|sprint-state.json' | wc -l
```

At evaluation time, two untracked files are currently present and are expected to persist through sprint completion unless the Sprint-14 commit(s) explicitly add them:

- `.council/sprint-prebrief/sprint-14.json` (shows as `?? ...`)
- `.harness/contracts/sprint-14.md` (shows as `?? ...`)

If these files are committed as part of sprint-14's "remaining intended changes," B4 passes cleanly. If either is left untracked at evaluation time, `git status --porcelain` will emit a `?? ...` line that the grep does NOT exclude, causing a false-FAIL (count > 0 when it should be 0).

The contract's "remaining intended changes" language implies these files will be committed (conventional harness behavior commits the contract and prebrief), so this is probably fine in practice. But the criterion does not explicitly name them as expected committed files, nor does the exclusion list cover them as acceptable dirty entries. A false-FAIL is possible if the evaluator runs before the Step-5 commit, or if the Generator omits them.

**Recommended fix (pick one):**
- Extend the grep exclusion: `grep -vE 'settings\.local\.json|progress\.md|sprint-state\.json|sprint-14\.'` — but this could mask actual unexpected content.
- Or: explicitly state in B4 that the evaluator runs AFTER the Step-5 commit lands and that the contract/prebrief files for sprint-14 are expected to be committed by then.
- Or: add `sprint-14.md` and `sprint-prebrief/sprint-14.json` to the Step-5 commit scope in the reference solution and clarify in B4 that untracked files must be zero at evaluation time.

**Issue #2 — SN1 pre-sprint baseline capture is implicit (non-blocking, advisory):**

The SN1 check requires comparing `git show HEAD:.council/audit-log.jsonl | wc -l` against "the pre-sprint working-copy line count." The pre-sprint working-copy count (currently 2347) is not explicitly recorded in the contract or in an artifact the evaluator reads. The evaluator must either (a) recall it from this review or (b) re-derive it at evaluation time — which is only possible if evaluated in the same session or if the working copy has not changed further. For robustness, the contract could record `2347` as the pre-sprint baseline line count alongside the other verified baselines in the Technical Notes section. Non-blocking for this sprint given minimal mode.

### Grader Split / Behavioral Floor

- Weight sum: 25 + 25 + 20 + 15 + 15 = **100%** (correct)
- Behavioral: 85% ≥ 60% floor (correct, no carve-out needed)
- Structural: 15% (S5 only)
- LLM-judge: 0%
- All behavioral criteria are exit-code or count deterministic

### Coverage of All 3 Deliverables

- (a) Audit-log commit: covered by B1 (25%)
- (b) Worktree gitlink removal: covered by B2 (25%) and B3 (20%)
- (c) Clean committed baseline: covered by B4 (15%) and S5 (15%)

All three deliverables have at least one criterion. Coverage is complete.

### Approved Criteria

B1, B2, B3, S5 are well-formed, testable, and unambiguous. SN1, SN2, SN3, SN4 are effective gates (with SN4's exit-code caveat already documented by the contract author).

### Feedback Summary

1. **B4 (non-blocking, fix recommended):** The grep exclusion in B4 will false-FAIL if `.council/sprint-prebrief/sprint-14.json` or `.harness/contracts/sprint-14.md` remain untracked at evaluation time. Explicitly commit these files in the reference solution or extend the exclusion pattern.
2. **SN1 (non-blocking, advisory):** Explicitly record the pre-sprint working-copy line count (2347) in the contract's Technical Notes as a concrete baseline value the evaluator can reference.

**Status: APPROVED**

The contract is sound and all pre-sprint baselines match reality. The two issues above are non-blocking: Issue #1 is a potential false-FAIL rather than a missed real failure, and Issue #2 is an advisory. The contract may proceed to implementation. The Generator should address Issue #1 (B4 exclusion gap) in the reference solution or criterion text before evaluation begins.
