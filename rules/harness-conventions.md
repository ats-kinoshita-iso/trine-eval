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
