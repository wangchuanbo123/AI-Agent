"""执行器接口定义。

执行器负责把 Agent 选择的动作转换成工具调用和观察结果。
"""

from __future__ import annotations

from typing import Protocol

from schemas.action import AgentAction
from schemas.observation import Observation


# 执行一个 Agent 动作的协议。
class Executor(Protocol):
    """执行 Agent 动作并返回观察结果。"""

    # 异步执行一个动作，并返回观察结果。
    async def aexecute(self, action: AgentAction) -> Observation:
        """异步执行一个动作。"""
