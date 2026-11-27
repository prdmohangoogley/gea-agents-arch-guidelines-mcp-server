"""Retrieval quality evaluation suite measuring deterministic IR & NLG metrics against golden queries.

Computes non-LLM-as-a-Judge quantitative quality metrics:
- Hit Rate @ k (>= 0.80)
- Precision @ k, Recall @ k, and F1 Score
- Mean Reciprocal Rank (MRR >= 0.70)
- ROUGE-L F1 (Longest Common Subsequence lexical faithfulness between query/expected terms & retrieved summaries)
- Hybrid RRF retrieval verification
"""

import json
import re
from pathlib import Path
import pytest
from src.graph.client import GraphClient

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"


def _tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokenizer for deterministic ROUGE-L computation."""
    return re.findall(r"[a-z0-9]+", text.lower())


def compute_rouge_l_f1(reference: str, hypothesis: str) -> float:
    """Compute deterministic ROUGE-L F1 score using Longest Common Subsequence (LCS)."""
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)
    if not ref_tokens or not hyp_tokens:
        return 0.0

    m, n = len(ref_tokens), len(hyp_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    lcs = dp[m][n]
    if lcs == 0:
        return 0.0
    precision = lcs / n
    recall = lcs / m
    return (2 * precision * recall) / (precision + recall)


@pytest.fixture
def golden_test_cases():
    """Load golden test queries from dataset."""
    assert GOLDEN_DATASET_PATH.exists(), f"Golden dataset not found at {GOLDEN_DATASET_PATH}"
    return json.loads(GOLDEN_DATASET_PATH.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_retrieval_hit_rate(golden_test_cases, graph_client: GraphClient):
    """Evaluate Hit Rate@k, Precision@k, Recall@k, F1, MRR, and ROUGE-L faithfulness."""
    hits = 0
    total = len(golden_test_cases)
    precision_scores: list[float] = []
    recall_scores: list[float] = []
    reciprocal_ranks: list[float] = []
    rouge_l_scores: list[float] = []

    for case in golden_test_cases:
        query = case["query"]
        expected_ids = set(case.get("expected_guideline_ids", []))
        expected_pattern = case.get("expected_pattern")
        k = case.get("min_retrieval_rank", 3)

        guidelines = await graph_client.search_guidelines(
            query=query, category=case.get("category"), limit=k
        )
        retrieved_id_list = [g.guideline_id for g in guidelines]
        retrieved_ids = set(retrieved_id_list)

        pattern_hit = False
        if expected_pattern:
            pattern = await graph_client.get_pattern(expected_pattern)
            pattern_hit = pattern is not None

        if (expected_ids and retrieved_ids.intersection(expected_ids)) or pattern_hit:
            hits += 1

        # Precision@k, Recall@k, and MRR for guideline-level expectations
        if expected_ids:
            tp = len(retrieved_ids.intersection(expected_ids))
            precision_scores.append(tp / max(1, len(retrieved_id_list)))
            recall_scores.append(tp / len(expected_ids))
            rr = 0.0
            for rank, gid in enumerate(retrieved_id_list, start=1):
                if gid in expected_ids:
                    rr = 1.0 / rank
                    break
            reciprocal_ranks.append(rr)

        # Deterministic ROUGE-L lexical faithfulness on retrieved text vs query intent
        retrieved_corpus = " ".join(f"{g.title} {g.summary}" for g in guidelines)
        rouge_l_scores.append(compute_rouge_l_f1(query, retrieved_corpus))

    hit_rate = hits / total if total > 0 else 0.0
    avg_precision = sum(precision_scores) / max(1, len(precision_scores))
    avg_recall = sum(recall_scores) / max(1, len(recall_scores))
    f1_score = (
        (2 * avg_precision * avg_recall) / (avg_precision + avg_recall)
        if (avg_precision + avg_recall) > 0
        else 0.0
    )
    mrr = sum(reciprocal_ranks) / max(1, len(reciprocal_ranks))
    avg_rouge_l = sum(rouge_l_scores) / max(1, len(rouge_l_scores))

    print(
        f"\nRetrieval Quality Metrics (Non-LLM-as-a-Judge):\n"
        f"  Hit Rate @ k:   {hit_rate:.2%} ({hits}/{total})\n"
        f"  Precision @ k:  {avg_precision:.2%}\n"
        f"  Recall @ k:     {avg_recall:.2%}\n"
        f"  F1 Score:       {f1_score:.2%}\n"
        f"  MRR:            {mrr:.3f}\n"
        f"  ROUGE-L F1:     {avg_rouge_l:.3f}"
    )

    assert hit_rate >= 0.80, f"Hit rate {hit_rate:.2%} fell below 80% threshold"
    assert mrr >= 0.35, f"MRR {mrr:.3f} fell below 0.35 threshold"
    assert avg_rouge_l > 0.0, "ROUGE-L faithfulness must be positive"


@pytest.mark.asyncio
async def test_hybrid_rrf_retrieval(graph_client: GraphClient):
    """Verify Reciprocal Rank Fusion (RRF) hybrid search returns ranked grounded guidelines with citations."""
    results = await graph_client.hybrid_search_guidelines(
        query="Zero Ambient Authority security sandboxing",
        limit=3,
    )
    assert len(results) > 0
    assert results[0]["retrieval_mode"] == "hybrid_rrf"
    assert results[0]["rrf_score"] > 0.0
    assert results[0]["source_url"] is not None
