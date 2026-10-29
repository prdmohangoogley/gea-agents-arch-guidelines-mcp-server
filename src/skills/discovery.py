"""Dynamic Discovery Engine scanning python plugins and .agents/skills/ directories."""

from __future__ import annotations

import importlib
import inspect
import logging
import os
import re
from pathlib import Path
from typing import Any
from src.skills.base import SkillPlugin, SkillManifest, SkillParameter

logger = logging.getLogger("skills-discovery")

_PLUGIN_REGISTRY: dict[str, SkillPlugin] = {}
_DYNAMIC_MANIFESTS: dict[str, SkillManifest] = {}
_INITIALIZED = False


def _parse_skill_md(file_path: Path) -> SkillManifest | None:
    """Parse an Antigravity agent SKILL.md file to extract metadata into a SkillManifest."""
    try:
        content = file_path.read_text(encoding="utf-8")
        # Check for YAML frontmatter between --- and ---
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not match:
            return None

        frontmatter_raw = match.group(1)
        body = match.group(2).strip()

        # Simple YAML key-value parser for frontmatter
        name_match = re.search(r"^name:\s*(.+)$", frontmatter_raw, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(?:>-\s*)?(.+?)(?=\n\w+:|$)", frontmatter_raw, re.DOTALL | re.MULTILINE)

        skill_name = name_match.group(1).strip() if name_match else file_path.parent.name
        description = desc_match.group(1).strip().replace("\n", " ") if desc_match else f"Skill {skill_name}"

        return SkillManifest(
            id=f"skill_{skill_name.replace('-', '_')}",
            name=skill_name.replace("-", " ").title(),
            version="1.0.0",
            category="workspace_skill",
            description=description,
            capabilities=[skill_name.replace("-", "_")],
            entrypoint="execute",
            context_token_estimate=250,
            sandbox_tier="workspace_write",
            parameters=[
                SkillParameter(name="input_payload", type="string", description=f"Input instructions for {skill_name}"),
            ],
            instructions=body[:500] if body else description,
        )
    except Exception as exc:
        logger.warning("Failed to parse %s: %s", file_path, exc)
        return None


def init_skills_registry() -> None:
    """Scan and initialize all python plugins in src/skills/plugins/ and .agents/skills/."""
    global _INITIALIZED, _PLUGIN_REGISTRY, _DYNAMIC_MANIFESTS
    if _INITIALIZED:
        return

    # 1. Scan src/skills/plugins/
    plugins_dir = Path(__file__).parent / "plugins"
    if plugins_dir.exists():
        for py_file in plugins_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            module_name = f"src.skills.plugins.{py_file.stem}"
            try:
                mod = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(mod, inspect.isclass):
                    if issubclass(obj, SkillPlugin) and obj is not SkillPlugin:
                        instance = obj()
                        manifest = instance.manifest
                        _PLUGIN_REGISTRY[manifest.id] = instance
                        _DYNAMIC_MANIFESTS[manifest.id] = manifest
            except Exception as e:
                logger.error("Error loading plugin %s: %s", module_name, e)

    # 2. Scan .agents/skills/ in project root
    workspace_root = Path(__file__).resolve().parents[2]
    agents_skills_dir = workspace_root / ".agents" / "skills"
    if agents_skills_dir.exists():
        for skill_dir in agents_skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    manifest = _parse_skill_md(skill_md)
                    if manifest and manifest.id not in _DYNAMIC_MANIFESTS:
                        _DYNAMIC_MANIFESTS[manifest.id] = manifest

    _INITIALIZED = True
    logger.info("Initialized Skills Registry with %d skills (%d active plugins)", len(_DYNAMIC_MANIFESTS), len(_PLUGIN_REGISTRY))


def get_plugin_instance(skill_id: str) -> SkillPlugin | None:
    """Retrieve an active executable SkillPlugin instance by ID."""
    init_skills_registry()
    return _PLUGIN_REGISTRY.get(skill_id)


def discover_all_skills() -> list[SkillManifest]:
    """Return all discovered SkillManifests across plugins and workspace skills."""
    init_skills_registry()
    return list(_DYNAMIC_MANIFESTS.values())


def get_manifest_by_id(skill_id: str) -> SkillManifest | None:
    """Retrieve a SkillManifest by its unique ID."""
    init_skills_registry()
    return _DYNAMIC_MANIFESTS.get(skill_id)
