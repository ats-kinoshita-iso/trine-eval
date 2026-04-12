# RAG System Evaluation Rubric

## Dimensions and Weights

### Retrieval Quality (30%)

| Score | Description |
|-------|-------------|
| 5 | Relevant chunks consistently in top-5. BM25 and dense retrieval complement each other. RRF fusion ranking works correctly. Pagination works for large result sets. |
| 4 | Relevant chunks in top-10. Retrieval methods work but fusion could be better. Pagination works. |
| 3 | Relevant chunks usually appear but ranking is inconsistent. One retrieval method may underperform. |
| 2 | Retrieval misses relevant chunks frequently. Ranking is poor. Results feel random. |
| 1 | Retrieval fails or returns irrelevant results consistently. |

### Answer Faithfulness (25%)

| Score | Description |
|-------|-------------|
| 5 | All generated answers grounded in retrieved chunks. No hallucinated facts. Citations point to actual source chunks. Answers acknowledge insufficient context. |
| 4 | Answers mostly grounded. Rare minor extrapolations. Citations accurate. |
| 3 | Answers generally correct but occasionally include facts not in retrieved chunks. Some citation errors. |
| 2 | Frequent hallucinations. Citations often wrong or missing. Answers contradict sources. |
| 1 | Answers are mostly fabricated with no grounding in retrieved content. |

### System Robustness (25%)

| Score | Description |
|-------|-------------|
| 5 | Handles empty retrieval gracefully. Malformed queries return helpful errors. Latency under thresholds. Concurrent queries work. |
| 4 | Good error handling. Latency acceptable. Minor issues under high concurrency. |
| 3 | Basic error handling. Some edge cases cause errors. Latency occasionally spikes. |
| 2 | Poor error handling. Crashes on malformed input. Latency often unacceptable. |
| 1 | System crashes on basic edge cases. No error handling. |

### Code & Architecture (20%)

| Score | Description |
|-------|-------------|
| 5 | Clean generator-evaluator separation. Pydantic models for all data contracts. Retrieval exposed as tools. Observability traces present. |
| 4 | Good separation. Models for most contracts. Retrieval mostly modular. Some observability. |
| 3 | Reasonable architecture. Some mixing of concerns. Partial data modeling. Limited observability. |
| 2 | Poor separation. Retrieval logic embedded in prompts. No data contracts. No observability. |
| 1 | Monolithic. No architectural boundaries. Impossible to test components independently. |

## Hard Thresholds

- **Retrieval Quality below 3/5 blocks everything.** Without good retrieval, answers cannot be faithful.
- **Faithfulness below 3/5 blocks everything.** Hallucinating answers is worse than no answer.

## Testing Tools

- **API tests:** pytest or curl for endpoint verification
- **Retrieval validation:** Direct database/vector store queries to verify chunk relevance
- **Faithfulness checks:** Compare generated answers against source chunks for grounding
- **Latency:** Time API responses under normal and concurrent load
- **Edge cases:** Empty queries, very long queries, queries with no relevant documents
