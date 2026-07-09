"""用于验证 MCP 工具加载的最小 MCP server。

通过 mcp_servers.json 运行它，可以把 add 和 multiply 暴露为 MCP 工具。
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("local_math")


# 把两个数字相加的 MCP 工具。
@mcp.tool()
def add(a: float, b: float) -> float:
    """把两个数字相加。"""
    return a + b


# 把两个数字相乘的 MCP 工具。
@mcp.tool()
def multiply(a: float, b: float) -> float:
    """把两个数字相乘。"""
    return a * b


if __name__ == "__main__":
    mcp.run()
