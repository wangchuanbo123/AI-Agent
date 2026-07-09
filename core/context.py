"""Agent 执行上下文。

上下文用于携带每个会话调用所需的轻量元数据。
"""

from __future__ import annotations

from dataclasses import dataclass


# 单次会话上下文；后续可加入用户、租户或权限等元数据。
@dataclass(frozen=True)
class AgentContext:
    """面向用户的一段会话执行上下文。"""

    thread_id: str = "default"
