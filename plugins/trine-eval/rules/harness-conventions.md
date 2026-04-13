---
paths: .harness/**
---

# Harness Conventions

- Sprint contracts are the source of truth for what "done" means
- JSON files in `.harness/` use 2-space indentation
- Eval results must include specific evidence for every FAIL grade
- Never modify a prior sprint's eval results — they are append-only records
- Communication between agents happens exclusively via files in `.harness/`
- The Evaluator never sees the Generator's reasoning trace

## JSON vs Markdown: When to Use Each

The harness uses two file formats for distinct purposes:

- **JSON** — Machine-readable structured state. Use for: `config.json`, `sprints.json`, `sprint-state.json`. JSON is preferred for structured data because models are less likely to inappropriately modify it during edits. JSON files are the source of truth for sprint status, configuration, and machine-parseable results.
- **Markdown** — Human-readable prose and notes. Use for: `progress.md`, `spec.md`, sprint contracts, eval reports. Markdown is better for session logs, design rationale, and any content that benefits from rich formatting.

Both formats should be kept in sync where they overlap (e.g., sprint status appears in both `sprint-state.json` and `progress.md`). When they conflict, JSON is authoritative for structured state.
