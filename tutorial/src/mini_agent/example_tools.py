"""Small teaching tools. Weather data here is deliberately simulated."""

from __future__ import annotations

from typing import Any

from .tools import Tool, ToolRegistry


def get_weather(city: str) -> dict[str, Any]:
    return {
        "city": city,
        "weather": "晴",
        "simulated": True,
        "notice": "教学模拟数据，不是实时天气",
    }


def validate_weather_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    if set(arguments) != {"city"}:
        raise ValueError("get_weather 只接受 city 参数")
    city = arguments["city"]
    if (
        not isinstance(city, str)
        or not city.strip()
        or len(city) > 80
        or any(ord(char) < 32 for char in city)
    ):
        raise ValueError("city 必须是 1–80 字符的非空字符串，且不含控制字符")
    return {"city": city.strip()}


def multiply(a: int | float, b: int | float) -> dict[str, int | float]:
    return {"a": a, "b": b, "product": a * b}


def validate_multiply_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    if set(arguments) != {"a", "b"}:
        raise ValueError("multiply 只接受 a 和 b 参数")
    for name in ("a", "b"):
        value = arguments[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} 必须是数字")
        if abs(value) > 1_000_000:
            raise ValueError(f"{name} 超出教学示例允许范围")
    return {"a": arguments["a"], "b": arguments["b"]}


def build_example_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="get_weather",
            description="查询教学用模拟天气；结果不是真实天气",
            parameters={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
            handler=get_weather,
            validate=validate_weather_arguments,
        )
    )
    registry.register(
        Tool(
            name="multiply",
            description="计算两个数字的乘积",
            parameters={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
            handler=multiply,
            validate=validate_multiply_arguments,
        )
    )
    return registry
