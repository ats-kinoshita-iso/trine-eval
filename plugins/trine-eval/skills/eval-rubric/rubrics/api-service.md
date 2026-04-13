# API Service Evaluation Rubric

## Dimensions and Weights

### Correctness (35%)

| Score | Description |
|-------|-------------|
| 5 | All endpoints return correct data. Status codes follow HTTP conventions. Validation rejects invalid payloads with 400 and descriptive errors. Pagination works correctly. |
| 4 | All core endpoints correct. Minor edge cases in validation. Status codes mostly correct. |
| 3 | Most endpoints work. One or two return wrong data or status codes. Validation has gaps. |
| 2 | Several endpoints broken. Wrong status codes common. Validation incomplete. |
| 1 | Most endpoints fail or return incorrect data. |

### Robustness (25%)

| Score | Description |
|-------|-------------|
| 5 | Handles concurrent requests. Malformed JSON returns 400. Missing fields return descriptive errors. DB errors return 500 with safe messages (no stack traces, no schema leaks). Rate limiting works if specified. |
| 4 | Good error handling. Concurrent requests work. Minor issues with edge cases. |
| 3 | Basic error handling. Some malformed inputs cause 500s. Concurrent access mostly works. |
| 2 | Poor error handling. Stack traces in responses. Concurrent issues. |
| 1 | Crashes on malformed input. Stack traces exposed. No concurrent safety. |

### API Design (20%)

| Score | Description |
|-------|-------------|
| 5 | Consistent naming conventions. Consistent response envelope. Clear documentation or discoverability. Versioning strategy clear. |
| 4 | Good consistency. Minor naming variations. Documentation present. |
| 3 | Mostly consistent. Some endpoints deviate from conventions. Partial documentation. |
| 2 | Inconsistent naming. No response envelope. No documentation. |
| 1 | No design consistency. Endpoints feel randomly structured. |

### Code Quality (20%)

| Score | Description |
|-------|-------------|
| 5 | Route handlers thin. Business logic in services. DB access in repositories. Clear module boundaries. Tests cover happy and error paths. |
| 4 | Good separation. Minor logic in handlers. Most paths tested. |
| 3 | Some separation. Business logic leaking into handlers. Partial tests. |
| 2 | Poor separation. Fat handlers with DB calls. Few tests. |
| 1 | Monolithic handlers. No architectural boundaries. No tests. |

## Hard Thresholds

- **Correctness below 3/5 blocks.** Core endpoints must return correct data.
- **Any endpoint returning a stack trace is automatic FAIL** for Robustness (score capped at 2).

## Testing Tools

- **Endpoint testing:** curl or httpie for manual requests
- **Status codes:** Verify correct codes for success (200/201), validation error (400), not found (404), server error (500)
- **Validation:** Send malformed JSON, missing required fields, wrong types, extra fields
- **Concurrency:** Send parallel requests with curl or a load testing tool
- **Error safety:** Verify no stack traces, internal paths, or schema details in error responses
- **Pagination:** Test with various page/limit combinations, including boundary values
