"""Unit tests for MultiModelRouter and Frontier Model Registry.

Asserts:
1. Registration of Gemini 3.1+, GPT, and Claude 5.* models.
2. Immediate rejection of legacy models (Gemini 2.5, 2.0, 1.5).
3. Correct model tier filtering and routing.
4. Resilient failover without legacy model degradation.
"""

import pytest

from src.models.router import (
    MODEL_REGISTRY,
    ModelFamily,
    ModelTier,
    MultiModelRouter,
    get_model_router,
)


def test_registry_contains_modern_models():
    """Verify that modern models from all three families are registered."""
    # Gemini 3.1+ & 4.0 Argon
    assert "gemini-4-argon" in MODEL_REGISTRY
    assert "gemini-3.1-pro" in MODEL_REGISTRY
    assert "gemini-3.5-pro" in MODEL_REGISTRY
    assert "gemini-3.1-flash" in MODEL_REGISTRY
    assert "gemini-3.1-ultra" in MODEL_REGISTRY

    # OpenAI GPT
    assert "gpt-5" in MODEL_REGISTRY
    assert "gpt-5-turbo" in MODEL_REGISTRY
    assert "o3" in MODEL_REGISTRY
    assert "o4-mini" in MODEL_REGISTRY

    # Anthropic Claude 5.*
    assert "claude-5-sonnet" in MODEL_REGISTRY
    assert "claude-5-opus" in MODEL_REGISTRY
    assert "claude-5-haiku" in MODEL_REGISTRY


def test_registry_strictly_excludes_legacy_models():
    """Verify that legacy models are nowhere in the registry."""
    legacy_keys = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gpt-3.5",
        "claude-2",
    ]
    for key in legacy_keys:
        assert key not in MODEL_REGISTRY


def test_validate_model_eligibility_rejects_legacy_models():
    """Verify that validate_model_eligibility raises ValueError on legacy models."""
    router = get_model_router()

    prohibited = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro-001",
        "gpt-3.5-turbo",
        "claude-2.1",
    ]
    for m in prohibited:
        with pytest.raises(ValueError, match="Legacy model .* is strictly prohibited"):
            router.validate_model_eligibility(m)


def test_validate_model_eligibility_accepts_modern_models():
    """Verify that modern models pass eligibility checks."""
    router = get_model_router()

    allowed = [
        "gemini-4-argon",
        "gemini-3.1-pro",
        "gemini-3.5-flash",
        "gpt-5",
        "o3",
        "claude-5-sonnet",
        "claude-5-opus",
    ]
    for m in allowed:
        # Should not raise
        router.validate_model_eligibility(m)


def test_tier_and_family_filtering():
    """Verify query filtering by tier and family."""
    router = get_model_router()

    # Judges
    judges = router.get_models_for_tier(ModelTier.JUDGE)
    judge_ids = [j.id for j in judges]
    assert "gemini-4-argon" in judge_ids
    assert "o3" in judge_ids

    # Claude family
    claude_models = router.get_models_for_family(ModelFamily.CLAUDE)
    claude_ids = [c.id for c in claude_models]
    assert "claude-5-sonnet" in claude_ids
    assert "claude-5-opus" in claude_ids

    # GPT family
    gpt_models = router.get_models_for_family(ModelFamily.GPT)
    gpt_ids = [g.id for g in gpt_models]
    assert "gpt-5" in gpt_ids
    assert "o3" in gpt_ids


@pytest.mark.asyncio
async def test_generate_content_router_fallback():
    """Verify dynamic generate_content returns valid response without legacy fallback."""
    router = get_model_router()

    # Prompt execution with default gemini-4-argon
    res = await router.generate_content(
        prompt="Explain Zero Ambient Authority in one sentence.",
        model_id="gemini-4-argon",
    )
    assert res is not None
    assert "model_used" in res
    assert "2.5" not in res["model_used"]
    assert "2.0" not in res["model_used"]
    assert "1.5" not in res["model_used"]
    assert res["status"] in ("success", "deterministic_fallback")
