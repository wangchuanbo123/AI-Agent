"""任务数据结构定义。

AgentTask 表示用户消息以及目标记忆线程。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# 提交给 Agent 的用户任务。
class AgentTask(BaseModel):
    """提交给 Agent 的用户任务。"""

    message: str = Field(..., min_length=1)
    thread_id: str = "default"
