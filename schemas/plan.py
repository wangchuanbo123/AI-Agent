"""计划数据结构定义。

这些 schema 预留给未来的 Plan&Execute 策略。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# 一个带完成状态的未来计划步骤。
class PlanStep(BaseModel):
    """未来 Plan&Execute 策略中的一个步骤。"""

    description: str
    done: bool = False


# 未来多步骤计划的容器。
class Plan(BaseModel):
    """为后续策略预留的轻量计划容器。"""

    steps: list[PlanStep] = Field(default_factory=list)
