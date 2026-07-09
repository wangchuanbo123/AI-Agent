"""Agent 抽象接口定义。

调用方和核心模块依赖这个契约，而不是直接依赖具体框架实现。
"""

from __future__ import annotations

from typing import Protocol

from schemas.result import AgentResult


# 所有 Agent 后端都应实现的公共协议。
class Agent(Protocol):
    """所有 Agent 实现共用的接口。"""

    # 在指定会话线程中处理一条用户消息。
    async def ainvoke(self, message: str, thread_id: str = "default") -> AgentResult:
        """异步运行 Agent 并处理一条用户消息。"""
