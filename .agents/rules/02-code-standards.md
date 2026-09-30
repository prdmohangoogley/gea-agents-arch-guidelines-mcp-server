# Code Standards & Quality Guidelines

## 1. Python Environment & Tooling
- Python Target: **Python >= 3.11**.
- Package & Virtual Environment Management: **UV** (using `pyproject.toml`).
- Linter & Formatter: **Ruff** (line length: 100, strict lint checks).
- Type Checker: **Mypy** with `check_untyped_defs = true`.

## 2. FastMCP Tool Design
- Every tool function MUST have a comprehensive docstring describing:
  - The purpose of the tool.
  - Explanation of each input parameter.
  - Expected return schema.
- Tools must use type annotations on all parameters and return types.
- Validate all incoming parameters using Pydantic v2 models.
- Handle exceptions gracefully, returning user-friendly error messages rather than raw stack traces.

## 3. Directory Layout & Imports
- Code files live in `src/` (FastMCP server) and `pipelines/` (NL2KG pipeline).
- Use absolute imports within packages (e.g., `from src.models.guideline import Guideline`).
- Keep `__init__.py` files minimal and explicit.

## 4. Testing & Evaluation
- Tests live in `tests/`.
- Unit tests (`tests/test_server.py`, `tests/test_pipeline.py`) test functionality in isolation using mocks (`pytest-mock`).
- Evaluation tests (`tests/evals/`) test retrieval accuracy, ranking, and response synthesis against `golden_dataset.json`.
- All async functions must be tested using `pytest-asyncio` (`@pytest.mark.asyncio`).
