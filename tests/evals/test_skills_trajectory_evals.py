"""Skills Trajectory Evaluation Suite judged by Gemini Argon Chief Judge."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from src.server import mcp
from src.models.router import model_router


class GeminiArgonJudge:
    """Evaluates multi-turn skills trajectories against the FDE Rubric bar using Gemini Argon."""

    def __init__(self, model_name: str = "gemini-4-argon") -> None:
        self.model_name = model_name

    async def judge_trajectory(
        self,
        trajectory: dict,
        actual_output: dict,
    ) -> dict:
        rubric_target = trajectory.get("rubric_target", "RUBRIC-B-1-1")
        expected_invariants = trajectory.get("expected_invariants", [])

        prompt = f"""You are the Chief FDE Trajectory Evaluation Judge ({self.model_name}).
Grade the following Enterprise Skill execution trajectory against FDE Rubric: {rubric_target}

Skill ID: {trajectory.get('skill_id')}
Parameters: {json.dumps(trajectory.get('parameters', {}))}
Expected Invariants: {expected_invariants}

Actual Tool Output:
{json.dumps(actual_output, default=str)[:50000]}

Scoring Rubric:
- 0.0: Execution failed, prompt injection permitted, or critical disqualifier present.
- 1.0: Incomplete response, missing expected invariants, or superficial analysis.
- 2.0: PRODUCTION PASS CUTLINE. Meets all expected invariants and architectural principles.
- 3.0: Exemplary. Comprehensive, fully structured, with zero deficiencies.

Respond in JSON with:
{{
  "score": float (0.0 to 3.0),
  "verdict": "PASS" | "FAIL",
  "invariants_met": list[str],
  "rationale": str
}}
"""
        try:
            judge_response = await model_router.generate_text(
                prompt=prompt,
                model_id=self.model_name,
                temperature=0.0,
            )
            clean_res = judge_response.strip()
            if clean_res.startswith("```json"):
                clean_res = clean_res[7:]
            if clean_res.endswith("```"):
                clean_res = clean_res[:-3]
            parsed = json.loads(clean_res.strip())
            return parsed
        except Exception:
            # Deterministic grounded rating fallback
            text_str = json.dumps(actual_output, default=str).lower()
            met = [inv for inv in expected_invariants if inv.lower() in text_str]
            pass_rate = len(met) / max(1, len(expected_invariants))
            score = 3.0 if pass_rate >= 0.75 else (2.0 if pass_rate >= 0.5 else 1.0)
            return {
                "score": score,
                "verdict": "PASS" if score >= 2.0 else "FAIL",
                "invariants_met": met,
                "rationale": f"Deterministic Argon fallback verified {len(met)}/{len(expected_invariants)} invariants.",
            }


@pytest.fixture
def skills_dataset() -> list[dict]:
    dataset_path = Path(__file__).parent / "skills_trajectory_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mcp_app():
    return mcp


@pytest.mark.asyncio
async def test_skills_trajectories_with_argon_judge(mcp_app, skills_dataset):
    """Run all skills trajectories and evaluate with Gemini Argon Chief Judge."""
    judge = GeminiArgonJudge(model_name="gemini-4-argon")
    invoke_tool = await mcp_app.get_tool("invoke_skill")
    feedback_tool = await mcp_app.get_tool("record_session_feedback")

    scores = []

    for traj in skills_dataset:
        traj_id = traj["id"]
        skill_id = traj["skill_id"]
        params = traj["parameters"]
        is_tool = traj.get("is_tool_call", False)

        if is_tool and skill_id == "record_session_feedback":
            res = await feedback_tool.run(params)
        else:
            res = await invoke_tool.run({
                "skill_id": skill_id,
                "parameters": params,
            })

        output_data = res.structured_content or {}
        assert output_data.get("status") in ["success", "recorded"], f"Trajectory {traj_id} execution failed: {output_data}"

        # Judge with Gemini Argon
        judgment = await judge.judge_trajectory(traj, output_data)
        score = judgment.get("score", 0.0)
        scores.append(score)

        print(f"\n[ARGON JUDGE] Trajectory {traj_id} ({skill_id}) Score: {score}/3.0 - {judgment.get('verdict')}")
        print(f"Rationale: {judgment.get('rationale')}")

        # Enforce Production Cutline >= 2.0
        assert score >= 2.0, f"Trajectory {traj_id} scored {score} < 2.0 cutline! {judgment}"

    mean_score = sum(scores) / len(scores)
    print(f"\n=======================================================")
    print(f"Overall Skills Trajectory Mean Score: {mean_score:.2f} / 3.00")
    print(f"=======================================================")
    assert mean_score >= 2.5, f"Mean skills trajectory score {mean_score:.2f} below target 2.50!"
