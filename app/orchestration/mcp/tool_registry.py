"""Registry for registering, discovering, and executing MCP tools."""

import logging
from typing import Any, Dict, List

from app.orchestration.mcp.base_tool import BaseMCPTool

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """Registry managing registration, listing, and execution of MCP tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseMCPTool] = {}

    def register(self, tool: BaseMCPTool) -> None:
        """Register a new MCP tool.

        Args:
            tool: An instance of BaseMCPTool.
        """
        if tool.name in self._tools:
            logger.warning("Overwriting registered tool: %s", tool.name)
        self._tools[tool.name] = tool
        logger.info("Registered MCP tool: %s", tool.name)

    def get_tool(self, name: str) -> BaseMCPTool | None:
        """Retrieve a registered tool by name.

        Args:
            name: The name of the tool.

        Returns:
            The BaseMCPTool instance, or None if not found.
        """
        return self._tools.get(name)

    def list_tools(self) -> List[BaseMCPTool]:
        """List all registered MCP tools.

        Returns:
            A list of all registered BaseMCPTool instances.
        """
        return list(self._tools.values())

    async def execute_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with input schema validation.

        Args:
            name: The name of the tool to run.
            arguments: Dictionary of arguments.

        Returns:
            Dict containing success status, output, and potential error.
        """
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' not found."}

        try:
            # Validate input using pydantic schema
            validated_args = tool.input_schema(**arguments)
            output = await tool.execute(**validated_args.model_dump())
            return {"success": True, "output": output}
        except Exception as e:
            logger.exception("Error executing tool %s: %s", name, str(e))
            return {"success": False, "error": f"Execution failed: {str(e)}"}
