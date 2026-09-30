"""Markdown extraction module for architectural guidelines."""

import re
from pathlib import Path
from typing import Any


def parse_markdown_sections(file_path: Path) -> dict[str, Any]:
    """Parse a markdown file into structured sections and metadata."""
    content = file_path.read_text(encoding="utf-8")
    filename = file_path.stem

    # Extract title from first # header or filename
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename.replace("-", " ").title()

    # Extract tags / topics if present
    tags = re.findall(r"#([a-zA-Z0-9_\-]+)", content)

    # Extract section headers
    sections = {}
    current_section = "intro"
    current_lines: list[str] = []

    for line in content.splitlines():
        header_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if header_match:
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
                current_lines = []
            current_section = header_match.group(2).strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return {
        "file_path": str(file_path),
        "filename": filename,
        "title": title,
        "tags": list(set(tags)),
        "sections": sections,
        "raw_text": content,
    }


def extract_all_documents(directory: Path) -> list[dict[str, Any]]:
    """Scan a directory for markdown files and parse each one."""
    if not directory.exists():
        return []
    markdown_files = sorted(list(directory.glob("*.md")) + list(directory.glob("**/*.md")))
    return [parse_markdown_sections(f) for f in markdown_files]
