# trine-eval

This repo is a Claude Code plugin marketplace containing the trine-eval plugin — a three-agent eval-driven development harness.

Plugin source is in `plugins/trine-eval/`.

## Skills

- `/harness-kickoff` — Initialize harness with a product prompt
- `/harness-sprint` — Run one sprint through contract→build→eval cycle
- `/harness-summary` — Generate cross-sprint evaluation report

The plugin's rubric inventory includes both `eval-harness` (meta layer — grades eval methodology such as contract format, grader hierarchy, and sprint workflow) and `harness-build` (runtime layer — grades agent runtime harnesses for conformance to playbook stages). See `plugins/trine-eval/skills/eval-rubric/rubrics/README.md` for the full decision guide on which rubric to use.

## Conventions

- Agent communication happens via files in `.harness/` only
- JSON for structured data, markdown for prose
- Sprint contracts are the source of truth for "done"
- Eval results are append-only — never modify prior sprints
