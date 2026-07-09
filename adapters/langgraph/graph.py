"""LangGraph ReAct 图组装模块。

构建第一版 Agent 使用的 Reason-Act-Observe 循环。
"""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


# 每轮图调用开始时使用的默认系统提示词。
SYSTEM_PROMPT = """You are a helpful agent.
Use tools when they are useful. If a tool returns an observation, use it to
produce the final answer. Keep answers concise and accurate."""


# 构建并编译支持可选工具的 ReAct 图。
def build_react_graph(
    llm: BaseChatModel,
    tools: Sequence[BaseTool],
    checkpointer: object,
) -> object:
    """构建一个支持可选工具的最小 ReAct 图。"""
    tool_list = list(tools)
    model = llm.bind_tools(tool_list) if tool_list else llm

    # 使用当前消息状态调用聊天模型。
    async def agent_node(state: MessagesState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        response = await model.ainvoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_edge(START, "agent")

    if tool_list:
        graph.add_node("tools", ToolNode(tool_list))
        graph.add_conditional_edges("agent", tools_condition)
        graph.add_edge("tools", "agent")
    else:
        graph.add_edge("agent", END)

    return graph.compile(checkpointer=checkpointer)
