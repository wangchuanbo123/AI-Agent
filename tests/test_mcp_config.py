"""MCP server 配置加载测试。"""

import json
import sys

from adapters.mcp.client import load_mcp_server_config


# 配置文件缺失时应禁用 MCP，且不抛出错误。
def test_missing_mcp_config_disables_mcp(tmp_path) -> None:
    assert load_mcp_server_config(str(tmp_path / "missing.json")) == {}


# Claude 风格的 mcpServers 配置应被规范化为 langchain-mcp-adapters 可用格式。
def test_loads_claude_style_mcp_config(tmp_path) -> None:
    config_path = tmp_path / "mcp_servers.json"
    config_path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "local_math": {
                        "command": "python",
                        "args": ["server.py"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    config = load_mcp_server_config(str(config_path))

    assert config["local_math"]["transport"] == "stdio"
    assert config["local_math"]["command"] == sys.executable
