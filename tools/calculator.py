"""计算器工具实现。

提供一个只支持算术表达式的安全求值器，并暴露为 LangChain 工具。
"""

from __future__ import annotations

import ast
import operator
from typing import Callable

from langchain_core.tools import tool


_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


# ReAct 图用于计算算术表达式的 LangChain 工具。
@tool
def calculator(expression: str) -> str:
    """计算基础算术表达式。"""
    try:
        value = _evaluate_expression(expression)
    except Exception as exc:  # noqa: BLE001 - 工具错误需要转成可读文本。
        return f"Calculator error: {exc}"
    return str(value)


# 解析并计算支持的算术表达式。
def _evaluate_expression(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


# 递归求值，仅允许数字 AST 节点和白名单运算符。
def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.BinOp):
        operator_func = _BINARY_OPERATORS.get(type(node.op))
        if operator_func is None:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        return operator_func(_eval_node(node.left), _eval_node(node.right))

    if isinstance(node, ast.UnaryOp):
        operator_func = _UNARY_OPERATORS.get(type(node.op))
        if operator_func is None:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        return operator_func(_eval_node(node.operand))

    raise ValueError(f"unsupported expression: {type(node).__name__}")
