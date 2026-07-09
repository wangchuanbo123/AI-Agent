"""内置计算器工具测试。"""

from tools.calculator import _evaluate_expression


# 验证标准运算符优先级。
def test_evaluate_expression() -> None:
    assert _evaluate_expression("2 + 3 * 4") == 14


# 验证不安全的 Python 表达式会被拒绝。
def test_rejects_function_calls() -> None:
    try:
        _evaluate_expression("__import__('os').system('echo bad')")
    except ValueError as exc:
        assert "unsupported expression" in str(exc)
    else:
        raise AssertionError("function calls should be rejected")
