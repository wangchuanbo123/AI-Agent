"""动作数据结构定义。

动作描述 Agent 选择的一次工具调用。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# 一次工具动作的结构化表示。
class AgentAction(BaseModel):
    """Agent 选择的工具动作。"""

    tool_name: str = Field(..., min_length=1)
    tool_input: dict[str, Any] = Field(default_factory=dict)
