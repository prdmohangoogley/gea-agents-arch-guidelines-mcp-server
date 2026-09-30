---
name: fastmcp-tool-dev
description: >-
  Develops, tests, and validates FastMCP tools, prompts, and resources for the Enterprise
  Agents Architectural Guidelines MCP Server. Use when adding new MCP tools, modifying tool
  signatures, or testing stdio/sse protocol compliance.
---

# FastMCP Tool Development Skill

This skill outlines the process for implementing, testing, and debugging Model Context Protocol (MCP) tools using the `FastMCP` framework.

## Steps for Adding a New MCP Tool

1. **Define Schema & Models**:
   - Add parameter models and response models in `src/models/`.
   - Ensure all models inherit from `pydantic.BaseModel` and include clear `Field` descriptions.

2. **Implement Tool Logic**:
   - Create or edit tool functions in `src/tools/`.
   - Decorate with `@mcp.tool()`:
     ```python
     @mcp.tool()
     async def search_guidelines(query: str, category: str | None = None) -> str:
         """Search architectural guidelines by topic or keyword."""
         ...
     ```

3. **Register Tool in Server**:
   - Ensure the tool module is imported and mounted in `src/server.py`.

4. **Test the Tool**:
   - Write unit tests in `tests/test_server.py`.
   - Test locally using stdio mode:
     ```bash
     python -m src.server --transport stdio
     ```
   - Test locally using SSE mode:
     ```bash
     python -m src.server --transport sse --port 8080
     curl http://localhost:8080/health
     ```
