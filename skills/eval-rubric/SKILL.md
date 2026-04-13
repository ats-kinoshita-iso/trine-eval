---
name: eval-rubric
description: Load domain-specific evaluation criteria and grading weights for the project type
allowed-tools: Read, Glob
---

# Eval Rubric

Load the appropriate evaluation rubric based on the project type.

## How to Use

1. Read `.harness/config.json` to get the `rubric` field
2. Read the matching rubric file from `skills/eval-rubric/rubrics/{rubric}.md`
3. Return the rubric content to the caller

The rubric defines:
- Quality dimensions with percentage weights
- Per-dimension scoring criteria (1-5 scale)
- Hard thresholds that cause automatic sprint failure
- Testing tools appropriate for the domain

## Available Rubrics

- `web-app` — Web applications (Playwright, browser console, responsive checks)
- `rag-system` — RAG/retrieval systems (faithfulness, retrieval quality, citations)
- `cli-tool` — Command-line tools (argument parsing, error messages, exit codes)
- `api-service` — REST/GraphQL APIs (status codes, validation, concurrency)
- `eval-harness` — Eval-driven development harnesses (methodology completeness, grading architecture, separation)

## Adding Custom Rubrics

Create a new markdown file in `skills/eval-rubric/rubrics/` following the same structure as existing rubrics. Update `.harness/config.json` to reference the new rubric name.
