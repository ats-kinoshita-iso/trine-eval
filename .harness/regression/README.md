# Regression Suite

This directory holds the harness's capability → regression graduation output.

## Purpose

The harness scores each sprint on its contract's criteria. Over time, certain criteria pass in the first evaluation round for several consecutive sprints — they saturate. Saturated criteria provide no improvement signal for *new* sprints, but they still need to keep passing: if a later sprint breaks a capability the harness thought was solid, it should fail loudly rather than silently proceed.

The regression suite in this directory is that "keep passing" track. It is the machine-readable output of saturation detection, and it gates every new sprint.

## Files

- **`regression.json`** — Append-only list of graduated task entries. Each entry is copied verbatim from the source sprint's `.harness/contracts/sprint-NN.tasks.json` and carries one added field, `graduated_from_sprint`, recording which sprint's eval first demonstrated saturation. Initialized as `{"tasks": []}`; `harness-summary` appends new entries on subsequent runs once criteria meet the graduation threshold (first-round-pass across 3+ consecutive sprints). Schema is documented in `rules/harness-conventions.md`.
- **`runs/`** — Timestamped results from the Step 0.5 Regression Gate. Each run writes a file named `run-<UTC-ISO8601>.json` recording which graduated tasks passed or failed and the stdout/stderr/exit-code captured per task.

## Lifecycle

1. **Graduation** — `skills/harness-summary/SKILL.md` identifies saturated criteria and appends their `tasks.json` entries to `regression.json`. Entries are never removed or rewritten by the harness; if an operator wants to retire a regression criterion, they edit this file by hand.
2. **Gating** — `skills/harness-sprint/SKILL.md` Step 0.5 reads `regression.json` at the start of every sprint (before contract negotiation) and runs each entry's `verification_command`. If any fail and `config.regression.fail_fast` is true (default), the sprint aborts with a list of failing `task_id`s and their `graduated_from_sprint` origin.
3. **Evidence** — The run file under `runs/` is the audit record: the exact command, its output, and its verdict. Step 0.5 uses the verbatim `verification_command` from the task, never a paraphrase, so the evidence here matches the evidence that justified graduation.

## Backward compatibility

If `regression.json` does not exist, or its `tasks` array is empty, Step 0.5 is a no-op. Projects that predate Phase 2 and never graduate a criterion experience no behavior change.
