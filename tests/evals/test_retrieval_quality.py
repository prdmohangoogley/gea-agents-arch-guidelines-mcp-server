"""Retrieval quality evaluation suite measuring hit rates against golden queries."""

import json
from pathlib import Path
import pytest
from src.graph.client import GraphClient

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"


@pytest.fixture
def golden_test_cases():
    """Load golden test queries from dataset."""
    assert GOLDEN_DATASET_PATH.exists(), f"Golden dataset not found at {GOLDEN_DATASET_PATH}"
    return json.loads(GOLDEN_DATASET_PATH.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_retrieval_hit_rate(golden_test_cases, graph_client: GraphClient):
    """Evaluate retrieval hit rate @ k against the golden dataset."""
    hits = 0
    total = len(golden_test_cases)

    for case in golden_test_cases:
        query = case["query"]
        expected_ids = set(case.get("expected_guideline_ids", []))
        expected_pattern = case.get("expected_pattern")

        # Query guidelines
        guidelines = await graph_client.search_guidelines(
            query=query, category=case.get("category"), limit=case.get("min_retrieval_rank", 3)
        )
        retrieved_ids = {g.guideline_id for g in guidelines}

        # Check if at least one expected guideline or pattern was retrieved
        pattern_hit = False
        if expected_pattern:
            pattern = await graph_client.get_pattern(expected_pattern)
            pattern_hit = pattern is not None

        if (expected_ids and retrieved_ids.intersection(expected_ids)) or pattern_hit:
            hits += 1

    hit_rate = hits / total if total > 0 else 0
    print(f"\nRetrieval Hit Rate: {hit_rate:.2%} ({hits}/{total})")
    assert hit_rate >= 0.80, f"Hit rate {hit_rate:.2%} fell below 80% threshold"
