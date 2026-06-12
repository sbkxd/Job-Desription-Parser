"""Abstract base class for all Model Context Protocol (MCP) tools."""

from abc import ABC, abstractmethod
from typing import Any, Type

from pydantic import BaseModel


class BaseMCPTool(ABC):
    """Abstract Base Class for Model Context Protocol (MCP) tools."""

    name: str
    description: str
    input_schema: Type[BaseModel]

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool logic with validated arguments.

        Args:
            **kwargs: Inputs matching the input_schema.

        Returns:
            The tool execution result payload.
        """
        pass
