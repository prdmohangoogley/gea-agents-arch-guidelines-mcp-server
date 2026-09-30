---
name: eval-harness
description: >-
  Runs evaluation benchmarks and validates retrieval accuracy, latency, and reasoning quality
  for the Enterprise Agents Architectural Guidelines MCP Server. Use when running regression
  evals, updating the golden evaluation dataset, or evaluating model retrieval precision.
---

# Evaluation Harness Skill

This skill explains how to benchmark and evaluate MCP server tool responses against the ground-truth golden dataset.

## Evaluation Workflow

1. **Review Golden Dataset**:
   - Golden queries and expected node traversals reside in `tests/evals/golden_dataset.json`.
   - Update queries when new guidelines or architectural patterns are added.

2. **Execute Evaluation Benchmark**:
   - Run the automated eval suite:
     ```bash
     pytest tests/evals/test_retrieval_quality.py -v
     ```

3. **Metrics Computed**:
   - **Retrieval Hit Rate @ k**: Percentage of relevant architectural patterns returned within top $k$ results.
   - **Tradeoff Completeness**: Verification that pros, cons, and mitigations are included in retrieved recommendations.
   - **Execution Latency**: Measurement of Spanner Graph traversal latency under concurrent client simulation.
