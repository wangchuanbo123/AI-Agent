"""MCP 工具加载辅助模块。

读取 MCP server 配置，创建 MultiServerMCPClient，并把 MCP 工具暴露给
LangGraph Agent。
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from config import Settings


# MCP loader 返回的工具包，用于让 client 与其工具保持同生命周期。
@dataclass
class MCPToolBundle:
    """已加载的 MCP client 和工具集合。

    保留 client 引用可以确保返回的工具在被 LangGraph 调用时仍能打开 MCP session。
    """

    client: MultiServerMCPClient | None
    tools: list[BaseTool]


# 加载全部已配置的 MCP 工具；未启用 MCP 时返回空工具包。
async def load_mcp_tools(settings: Settings) -> MCPToolBundle:
    """如果配置文件存在，则从 settings.mcp_config_path 加载 MCP 工具。"""
    server_config = load_mcp_server_config(settings.mcp_config_path)
    if not server_config:
        return MCPToolBundle(client=None, tools=[])

    client = MultiServerMCPClient(server_config)
    tools = await client.get_tools()
    return MCPToolBundle(client=client, tools=tools)


# 加载并规范化 MCP server 配置文件。
def load_mcp_server_config(config_path: str) -> dict[str, dict[str, Any]]:
    """读取 MCP server 配置。

    支持普通映射，也支持 Claude 风格的 {"mcpServers": {...}} 文件。
    配置文件不存在时表示 MCP 未启用。
    """
    path = Path(config_path)
    if not path.exists():
        return {}

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("MCP config must be a JSON object")

    servers = raw.get("mcpServers", raw)
    if not isinstance(servers, Mapping):
        raise ValueError("MCP config 'mcpServers' must be a JSON object")

    base_dir = path.resolve().parent
    normalized: dict[str, dict[str, Any]] = {}
    for name, value in servers.items():
        if not isinstance(name, str) or not isinstance(value, Mapping):
            raise ValueError("Each MCP server must be a named JSON object")
        server = dict(value)
        server.setdefault("transport", "stdio" if "command" in server else "http")
        if server.get("transport") == "stdio" and server.get("command") == "python":
            server["command"] = sys.executable
        if server.get("transport") == "stdio" and isinstance(server.get("args"), list):
            server["args"] = [_resolve_relative_arg(arg, base_dir) for arg in server["args"]]
        normalized[name] = server

    return normalized


# 尽可能把 stdio 参数中的相对路径转换成绝对路径。
def _resolve_relative_arg(value: object, base_dir: Path) -> object:
    if not isinstance(value, str):
        return value

    candidate = Path(value)
    if candidate.is_absolute():
        return value

    looks_like_path = candidate.suffix or "/" in value or "\\" in value
    if not looks_like_path:
        return value

    resolved = (base_dir / candidate).resolve()
    return str(resolved) if resolved.exists() else value
