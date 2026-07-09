"""MCP 适配器包。

导出把外部 MCP 工具加载成 LangChain 兼容工具的辅助函数。
"""

from adapters.mcp.client import MCPToolBundle, load_mcp_tools

__all__ = ["MCPToolBundle", "load_mcp_tools"]
