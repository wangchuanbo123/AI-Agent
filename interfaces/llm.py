"""LLM 抽象接口定义。

这些契约让核心 Agent 可以在 Ollama、OpenAI-compatible 和未来模型后端之间切换。
"""

from __future__ import annotations

from typing import Protocol, Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool


# 用于创建聊天模型实例的工厂协议。
class LLMFactory(Protocol):
    """能够为 Agent 创建聊天模型的工厂。"""

    # 创建一个 Agent 可以调用的聊天模型。
    def create(self) -> BaseChatModel:
        """创建聊天模型实例。"""


# 支持绑定工具的聊天模型协议。
class ToolBindableLLM(Protocol):
    """使用工具的 Agent 所需的聊天模型行为。"""

    # 绑定工具，并返回能够产生工具调用的模型包装器。
    def bind_tools(self, tools: Sequence[BaseTool]) -> BaseChatModel:
        """返回一个可以调用工具的模型包装器。"""
