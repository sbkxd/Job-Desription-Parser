"""MCP tool framework and tools package initialization."""

from app.orchestration.mcp.base_tool import BaseMCPTool
from app.orchestration.mcp.fetch_jd import FetchJDTool
from app.orchestration.mcp.lookup_taxonomy import LookupTaxonomyTool
from app.orchestration.mcp.run_ner import RunNERTool
from app.orchestration.mcp.save_parsed_jd import SaveParsedJDTool
from app.orchestration.mcp.tool_registry import MCPToolRegistry


def register_all_tools(registry: MCPToolRegistry) -> None:
    """Helper function to register all standard MCP tools into a registry.

    Args:
        registry: The target MCPToolRegistry.
    """
    registry.register(FetchJDTool())
    registry.register(RunNERTool())
    registry.register(LookupTaxonomyTool())
    registry.register(SaveParsedJDTool())


__all__ = [
    "BaseMCPTool",
    "MCPToolRegistry",
    "FetchJDTool",
    "RunNERTool",
    "LookupTaxonomyTool",
    "SaveParsedJDTool",
    "register_all_tools",
]
