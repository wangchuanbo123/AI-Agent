"""Agent 运行配置。

本模块集中读取环境变量和 .env 文件，避免业务代码直接依赖具体环境变量名称。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv


# 当前支持的模型提供方名称。
ModelProvider = Literal["ollama", "openai_compatible"]


# Agent 运行时配置，包含本地开发和模型提供方切换所需的字段。
@dataclass(frozen=True)
class Settings:
    """从环境变量加载的运行时配置。"""

    model_provider: ModelProvider = "ollama"
    ollama_model: str = "qwen3:4b"
    ollama_base_url: str = "http://localhost:11434"
    openai_compatible_model: str = ""
    openai_compatible_base_url: str = ""
    openai_compatible_api_key: str = ""
    agent_temperature: float = 0.0
    default_thread_id: str = "default"
    mcp_config_path: str = "mcp_servers.json"

    # 从 .env 和进程环境变量中加载配置。
    @classmethod
    def from_env(cls) -> "Settings":
        """从 .env 和系统环境变量创建配置对象。"""
        load_dotenv()

        provider = os.getenv("MODEL_PROVIDER", cls.model_provider).strip().lower()
        if provider not in ("ollama", "openai_compatible"):
            raise ValueError(
                "MODEL_PROVIDER must be one of: ollama, openai_compatible"
            )

        return cls(
            model_provider=provider,  # type: ignore[arg-type]  # provider 已在上方校验。
            ollama_model=os.getenv("OLLAMA_MODEL", cls.ollama_model).strip(),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", cls.ollama_base_url).strip(),
            openai_compatible_model=os.getenv(
                "OPENAI_COMPATIBLE_MODEL", cls.openai_compatible_model
            ).strip(),
            openai_compatible_base_url=os.getenv(
                "OPENAI_COMPATIBLE_BASE_URL", cls.openai_compatible_base_url
            ).strip(),
            openai_compatible_api_key=os.getenv(
                "OPENAI_COMPATIBLE_API_KEY", cls.openai_compatible_api_key
            ).strip(),
            agent_temperature=float(
                os.getenv("AGENT_TEMPERATURE", str(cls.agent_temperature))
            ),
            default_thread_id=os.getenv(
                "AGENT_THREAD_ID", cls.default_thread_id
            ).strip(),
            mcp_config_path=os.getenv("MCP_CONFIG_PATH", cls.mcp_config_path).strip(),
        )
