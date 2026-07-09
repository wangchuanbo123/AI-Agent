"""LangChain 适配器包。

导出基于 LangChain provider 集成构建的模型工厂工具。
"""

from adapters.langchain.llm import create_chat_model

__all__ = ["create_chat_model"]
