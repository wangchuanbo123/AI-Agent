"""Agent CLI 入口。

本模块负责把配置、聊天模型、短期记忆、内置工具和可选 MCP 工具组装成
一个可交互的命令行应用。
"""

from __future__ import annotations

import asyncio
import sys

from adapters.langchain import create_chat_model
from adapters.langgraph import build_react_graph
from adapters.mcp import load_mcp_tools
from config import Settings
from core.agent import LangGraphAgent
from memory.short_term import create_short_term_memory
from tools.calculator import calculator


# 组装运行时组件，并启动交互式 Agent 会话。
async def async_main() -> None:
    """运行交互式 Agent 命令行。"""
    settings = Settings.from_env()
    memory = create_short_term_memory()
    llm = create_chat_model(settings)
    mcp_bundle = await load_mcp_tools(settings)
    tools = [calculator, *mcp_bundle.tools]
    graph = build_react_graph(llm, tools, memory.checkpointer)
    agent = LangGraphAgent(graph=graph, memory=memory)

    thread_id = settings.default_thread_id
    print(
        f"Agent ready: provider={settings.model_provider}, "
        f"model={_display_model(settings)}, tools={len(tools)}, thread={thread_id}"
    )
    print("Type 'exit' or 'quit' to stop. Use '/thread NAME' to switch memory thread.")

    while True:
        try:
            user_input = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            return
        if user_input.startswith("/thread "):
            thread_id = user_input.removeprefix("/thread ").strip() or thread_id
            print(f"Switched to thread: {thread_id}")
            continue

        try:
            result = await agent.ainvoke(user_input, thread_id=thread_id)
        except Exception as exc:  # noqa: BLE001 - CLI 需要带上下文处理失败。
            print(f"Agent error: {exc}")
            print("Check that Ollama is running and the configured model is pulled.")
            continue

        print(f"Agent> {result.content}")


# 把异步 CLI 包装成普通 Python 入口函数。
def main() -> None:
    """运行 Agent 应用。"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        sys.exit(130)


# 返回当前配置的模型名称，用于启动时展示。
def _display_model(settings: Settings) -> str:
    if settings.model_provider == "ollama":
        return settings.ollama_model
    return settings.openai_compatible_model


if __name__ == "__main__":
    main()
