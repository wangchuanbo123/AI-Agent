"""Agent 核心包装器。

本模块把编译后的 LangGraph 图包装成项目统一的 Agent 调用形态，
自身不负责创建具体模型提供方。
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from memory.short_term import LangGraphShortTermMemory
from schemas.result import AgentResult


# 隐藏 LangGraph 调用和结果解析细节的 Agent 门面。
class LangGraphAgent:
    """编译后的 LangGraph ReAct 图的轻量核心包装器。"""

    # 保存编译后的图和对应的短期记忆后端。
    def __init__(self, graph: object, memory: LangGraphShortTermMemory) -> None:
        self._graph = graph
        self._memory = memory

    # 向指定会话线程追加用户消息，并返回最新助手回答。
    async def ainvoke(self, message: str, thread_id: str = "default") -> AgentResult:
        """调用图并返回最新的助手消息。"""
        result = await self._graph.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            self._memory.config_for(thread_id),
        )
        content = _last_ai_content(result.get("messages", []))
        return AgentResult(content=content, thread_id=thread_id, raw=result)


# 从 LangGraph 的消息列表中找到最后一条 AI 消息。
def _last_ai_content(messages: list[object]) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            return _content_to_text(message.content)
    return ""


# 把 LangChain 返回的字符串或分块内容统一转换为纯文本。
def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)
