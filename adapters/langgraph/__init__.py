"""LangGraph 适配器包。

导出图构建器，把核心 Agent 行为转换成 LangGraph 流程。
"""

from adapters.langgraph.graph import build_react_graph

__all__ = ["build_react_graph"]
