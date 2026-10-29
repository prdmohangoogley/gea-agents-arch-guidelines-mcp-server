"""FastMCP Tools package."""

from src.tools.evolution import register_evolution_tools
from src.tools.fde_governance import register_fde_governance_tools
from src.tools.guidelines import register_guideline_tools
from src.tools.health import register_health_tools
from src.tools.patterns import register_pattern_tools
from src.tools.skills import register_skill_tools
from src.tools.specs import register_spec_tools

__all__ = [
    "register_guideline_tools",
    "register_pattern_tools",
    "register_health_tools",
    "register_fde_governance_tools",
    "register_skill_tools",
    "register_evolution_tools",
    "register_spec_tools",
]
