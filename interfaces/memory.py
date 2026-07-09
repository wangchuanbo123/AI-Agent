"""记忆接口定义。

第一版只定义短期记忆契约；长期记忆和向量记忆可以后续在这个边界后扩展。
"""

from __future__ import annotations

from typing import Protocol


# 按会话线程隔离的短期图记忆协议。
class ShortTermMemory(Protocol):
    """图 checkpointer 使用的线程级短期记忆。"""

    # 返回某个会话线程对应的图运行配置。
    def config_for(self, thread_id: str) -> dict:
        """返回指定会话线程的图配置。"""
