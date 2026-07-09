"""工具接口定义。

工具可以由本地代码实现，也可以从外部 MCP server 加载。
"""

from __future__ import annotations

from typing import Protocol


# 业务工具的最小协议。
class Tool(Protocol):
    """业务工具使用的最小工具契约。"""

    name: str
    description: str

    # 使用结构化输入运行工具。
    def invoke(self, input_data: object) -> object:
        """使用结构化输入执行工具。"""
