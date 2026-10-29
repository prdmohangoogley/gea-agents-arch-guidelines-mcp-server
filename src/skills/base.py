"""Base definitions, data structures, and plugin contracts for the Enterprise Skills Engine."""

from __future__ import annotations

import abc
import time
from typing import Any, Optional
from pydantic import BaseModel, Field


class SkillParameter(BaseModel):
    """Parameter specification for an enterprise skill."""
    name: str
    type: str  # 'string', 'integer', 'boolean', 'dict', 'list'
    description: str
    required: bool = True
    default: Any = None


class SkillManifest(BaseModel):
    """Manifest describing a skill for Tier 1 and Tier 2 Progressive Disclosure."""
    id: str
    name: str
    version: str = "1.0.0"
    category: str = "architecture"  # 'architecture', 'governance', 'workflow', 'security', 'knowledge_management', 'devops'
    description: str
    capabilities: list[str] = Field(default_factory=list)
    entrypoint: str
    context_token_estimate: int = 200
    sandbox_tier: str = "read_only"  # 'read_only', 'workspace_write', 'analytics_read', 'infra_deploy'
    parameters: list[SkillParameter] = Field(default_factory=list)
    instructions: str = ""


class SkillResult(BaseModel):
    """Structured execution result returned by a skill plugin."""
    status: str = "success"  # 'success', 'error', 'blocked', 'needs_clarification'
    skill_id: str
    latency_ms: float = 0.0
    data: dict[str, Any] = Field(default_factory=dict)
    token_metrics: dict[str, int] = Field(default_factory=lambda: {
        "prompt_tokens_estimated": 0,
        "completion_tokens_estimated": 0,
        "tokens_saved_by_cache": 0,
    })
    error_message: Optional[str] = None


class SkillExecutionContext(BaseModel):
    """Runtime execution context provided to skill execution."""
    caller_identity: str = "anonymous"
    session_id: str = "default-session"
    trace_id: str = ""
    sandbox_tier: str = "read_only"
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


class SkillPlugin(abc.ABC):
    """Abstract base class for all Enterprise Skill Plugins."""

    @property
    @abc.abstractmethod
    def manifest(self) -> SkillManifest:
        """Return the complete SkillManifest for progressive disclosure."""
        pass

    @abc.abstractmethod
    async def execute(
        self,
        context: SkillExecutionContext,
        parameters: dict[str, Any],
    ) -> SkillResult:
        """Execute the skill with provided parameters and return a structured SkillResult."""
        pass

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimator: 1 token ~= 4 chars."""
        return max(1, len(text) // 4)
