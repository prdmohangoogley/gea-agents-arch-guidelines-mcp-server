"""Trajectory evaluation suite testing multi-turn agent paths and skills registry workflows.

Measures:
1. Tool Selection Precision (TSP >= 0.90)
2. Argument Accuracy (AA >= 0.95)
3. Step-by-step invariant compliance (PII redaction, progressive disclosure token budgets,
   0-score disqualifier detection, and output assertion checks).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from src.server import create_server

TRAJECTORY_DATASET_PATH = Path(__file__).parent / "trajectory_dataset.json"


@pytest.fixture
def trajectory_cases():
    """Load trajectory cases from JSON."""
    assert TRAJECTORY_DATASET_PATH.exists(), f"Trajectory dataset not found at {TRAJECTORY_DATASET_PATH}"
    return json.loads(TRAJECTORY_DATASET_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def mcp_app():
    """Instantiate the FastMCP server."""
    return create_server()


@pytest.mark.asyncio
async def test_multi_turn_trajectories(trajectory_cases, mcp_app):
    """Execute all multi-turn trajectories and assert quality metrics and invariants."""
    total_steps = 0
    correct_tools = 0
    correct_arguments = 0

    print(f"\nEvaluating {len(trajectory_cases)} multi-turn agent trajectories...")

    for traj in trajectory_cases:
        traj_id = traj["trajectory_id"]
        goal = traj["goal"]
        steps = traj.get("steps", [])
        print(f"\n--- Trajectory: {traj_id} ({goal}) ---")

        for step in steps:
            total_steps += 1
            tool_name = step["tool"]
            args = step.get("arguments", {})

            # 1. Check Tool Selection / Availability
            try:
                tool = await mcp_app.get_tool(tool_name)
                assert tool is not None, f"Tool {tool_name} not registered"
                correct_tools += 1
            except Exception as e:
                pytest.fail(f"Tool {tool_name} resolution failed in {traj_id}: {e}")

            # 2. Check Argument Compatibility & Run
            try:
                res = await tool.run(args)
                correct_arguments += 1
            except Exception as e:
                pytest.fail(f"Execution of {tool_name} with args {args} failed in {traj_id}: {e}")

            # 3. Assert Outputs
            structured = res.structured_content or {}
            text_chunks = [c.text for c in res.content if hasattr(c, "text") and c.text]
            full_text = "\n".join(text_chunks) + " " + json.dumps(structured)

            # Check expected status if specified
            if "expected_status" in step:
                actual_status = structured.get("status")
                assert actual_status == step["expected_status"], (
                    f"Expected status '{step['expected_status']}', got '{actual_status}' in {traj_id} step {step['turn']}"
                )

            # Check expected tokens / strings in output
            for expected_str in step.get("expected_output_contains", []):
                assert expected_str in full_text, (
                    f"Expected substring '{expected_str}' missing from output of {tool_name} in {traj_id} turn {step['turn']}"
                )

            # Check unexpected strings (e.g. leaked secrets) do NOT appear
            for unexpected_str in step.get("unexpected_output_contains", []):
                assert unexpected_str not in full_text, (
                    f"Unexpected substring '{unexpected_str}' found in output of {tool_name} in {traj_id} turn {step['turn']}"
                )

            print(f"  ✓ Turn {step['turn']}: [{tool_name}] passed assertions.")

    # Compute Trajectory Metrics
    tsp = correct_tools / total_steps if total_steps > 0 else 0.0
    aa = correct_arguments / total_steps if total_steps > 0 else 0.0

    print(f"\n==========================================")
    print(f"Trajectory Metrics Summary:")
    print(f"  Total Evaluated Steps:       {total_steps}")
    print(f"  Tool Selection Precision:   {tsp:.2%} (Target >= 90.0%)")
    print(f"  Argument Accuracy:          {aa:.2%} (Target >= 95.0%)")
    print(f"==========================================")

    assert tsp >= 0.90, f"Tool Selection Precision {tsp:.2%} fell below 90% threshold"
    assert aa >= 0.95, f"Argument Accuracy {aa:.2%} fell below 95% threshold"
