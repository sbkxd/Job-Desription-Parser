"""Unit tests for the MCP Tool Framework (Milestone 7.2 & 7.13)."""

from typing import Any

import pytest
from pydantic import BaseModel, Field

from app.orchestration.mcp.base_tool import BaseMCPTool
from app.orchestration.mcp.tool_registry import MCPToolRegistry


class DummyInput(BaseModel):
    value: str = Field(..., description="A dummy input value")


class DummyTool(BaseMCPTool):
    name: str = "dummy_tool"
    description: str = "A dummy tool for framework testing"
    input_schema = DummyInput

    async def execute(self, value: str, **kwargs: Any) -> str:
        return f"Echo: {value}"


def test_mcp_tool_properties() -> None:
    tool = DummyTool()
    assert tool.name == "dummy_tool"
    assert tool.description == "A dummy tool for framework testing"
    assert tool.input_schema == DummyInput


@pytest.mark.asyncio
async def test_tool_registry_operations() -> None:
    registry = MCPToolRegistry()
    tool = DummyTool()

    # Register
    registry.register(tool)
    assert registry.get_tool("dummy_tool") == tool

    # List
    tools = registry.list_tools()
    assert tool in tools

    # Execute successfully
    res = await registry.execute_tool("dummy_tool", {"value": "hello"})
    assert res["success"] is True
    assert res["output"] == "Echo: hello"

    # Execute with invalid schema arguments (triggers validation error)
    res2 = await registry.execute_tool("dummy_tool", {})
    assert res2["success"] is False
    assert "validation" in res2["error"].lower()

    # Execute non-existent tool
    res3 = await registry.execute_tool("missing", {})
    assert res3["success"] is False
    assert "not found" in res3["error"].lower()
