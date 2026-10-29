"""Enterprise Multi-Model Router and Model Registry.

Supports Gemini 3.1+ (including Gemini 4 Argon), OpenAI GPT models (GPT-5, o3, o4-mini),
and Anthropic Claude 5.* models (Sonnet, Opus, Haiku).
Strictly eliminates legacy models (Gemini 2.5, 2.0, 1.5).
"""

from .router import (
    ModelFamily,
    ModelTier,
    ModelSpec,
    MODEL_REGISTRY,
    MultiModelRouter,
    get_model_router,
)

__all__ = [
    "ModelFamily",
    "ModelTier",
    "ModelSpec",
    "MODEL_REGISTRY",
    "MultiModelRouter",
    "get_model_router",
]
