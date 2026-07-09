"""短期记忆实现。

LangGraph 的内存 checkpointer 会在 Python 进程存活期间，按 thread_id 保存会话状态。
"""

from __future__ import annotations

try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:  # pragma: no cover - 兼容较旧版本的 LangGraph。
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver


# 基于 LangGraph InMemorySaver 的短期记忆包装器。
class LangGraphShortTermMemory:
    """LangGraph 运行时使用的线程级进程内记忆。

    checkpointer 会以 thread_id 为键保存图状态快照。这样在 Python 进程存活期间，
    同一个 thread_id 可以保持对话连续性。它不是长期记忆，进程重启后不会保留。
    """

    # 创建底层的 LangGraph 内存 checkpointer。
    def __init__(self) -> None:
        self.checkpointer = InMemorySaver()

    # 构建用于选择会话线程的 LangGraph 配置。
    def config_for(self, thread_id: str) -> dict:
        """返回选中某个会话线程的 LangGraph 配置。"""
        return {"configurable": {"thread_id": thread_id}}


# 创建默认短期记忆后端。
def create_short_term_memory() -> LangGraphShortTermMemory:
    """创建默认的短期记忆后端。"""
    return LangGraphShortTermMemory()
