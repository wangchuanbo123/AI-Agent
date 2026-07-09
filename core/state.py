"""Agent 运行状态。

定义图节点之间传递的状态结构。
"""

from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import BaseMessage


# LangGraph 节点之间传递的消息状态。
class AgentState(TypedDict):
    """贯穿 Agent 图的消息状态。"""

    messages: list[BaseMessage]
