"""LangChain 聊天模型工厂。

根据配置创建模型后端，同时把 provider 细节隔离在核心 Agent 实现之外。
"""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from config import Settings


# 为当前 provider 创建配置好的聊天模型。
def create_chat_model(settings: Settings) -> BaseChatModel:
    """创建已配置的聊天模型。"""
    if settings.model_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=settings.agent_temperature,
        )

    if settings.model_provider == "openai_compatible":
        _validate_openai_compatible(settings)
        return ChatOpenAI(
            model=settings.openai_compatible_model,
            base_url=settings.openai_compatible_base_url,
            api_key=settings.openai_compatible_api_key,
            temperature=settings.agent_temperature,
        )

    raise ValueError(f"Unsupported model provider: {settings.model_provider}")


# 确认 OpenAI-compatible 模式具备所有必要连接配置。
def _validate_openai_compatible(settings: Settings) -> None:
    missing: list[str] = []
    if not settings.openai_compatible_model:
        missing.append("OPENAI_COMPATIBLE_MODEL")
    if not settings.openai_compatible_base_url:
        missing.append("OPENAI_COMPATIBLE_BASE_URL")
    if not settings.openai_compatible_api_key:
        missing.append("OPENAI_COMPATIBLE_API_KEY")
    if missing:
        raise ValueError(
            "OpenAI-compatible provider is missing: " + ", ".join(missing)
        )
