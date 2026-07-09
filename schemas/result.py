"""结果数据结构定义。

AgentResult 是返回给调用方的稳定输出结构。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# Agent 门面返回的最终规范化结果。
class AgentResult(BaseModel):
    """Agent 包装器返回的最终结果。"""

    content: str
    thread_id: str
    raw: dict[str, Any] = Field(default_factory=dict)
