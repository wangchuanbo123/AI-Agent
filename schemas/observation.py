"""观察结果数据结构定义。

观察结果用于承载工具或执行器返回的输出。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


# 一次工具或执行器动作的结构化结果。
class Observation(BaseModel):
    """工具或执行器返回的结果。"""

    action_name: str
    output: Any
    is_error: bool = False
