"""执行策略定义。

第一版只启用 ReAct；Plan&Execute 和 Hybrid 策略可以后续在这里扩展。
"""

from __future__ import annotations

from enum import StrEnum


# Agent 支持的执行策略名称。
class ExecutionStrategy(StrEnum):
    """Agent 支持的执行策略。"""

    REACT = "react"
