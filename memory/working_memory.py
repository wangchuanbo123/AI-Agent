"""工作记忆实现。

本模块用于保存未来更复杂 Agent 循环中的临时结构化草稿数据；
第一版主流程暂未使用它。
"""

from __future__ import annotations

from dataclasses import dataclass, field


# 简单的键值对草稿容器。
@dataclass
class WorkingMemory:
    """用于未来非消息运行状态的小型草稿区。"""

    values: dict[str, object] = field(default_factory=dict)
