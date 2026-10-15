"""Tool definitions, validation, registration, and execution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from .models import ToolCall, ToolSpec


Validator = Callable[[dict[str, Any]], dict[str, Any]]
Handler = Callable[..., Any]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Handler
    validate: Validator
    requires_approval: bool = False

    def public_spec(self) -> ToolSpec:
        """Return only the description the model is allowed to see."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass(frozen=True)
class PreparedToolCall:
    call_id: str
    tool: Tool
    arguments: dict[str, Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if not tool.name or tool.name in self._tools:
            raise ValueError(f"工具名为空或重复：{tool.name!r}")
        self._tools[tool.name] = tool

    def public_specs(self) -> list[ToolSpec]:
        return [tool.public_spec() for tool in self._tools.values()]

    def prepare(self, call: ToolCall) -> PreparedToolCall:
        tool = self._tools.get(call.name)
        if tool is None:
            raise ValueError(f"拒绝未注册的工具：{call.name!r}")
        if not call.id:
            raise ValueError("工具调用 ID 不能为空")
        try:
            raw_arguments = json.loads(call.arguments)
        except json.JSONDecodeError as exc:
            raise ValueError(f"工具参数不是合法 JSON：{exc.msg}") from exc
        if not isinstance(raw_arguments, dict):
            raise ValueError("工具参数必须是 JSON 对象")
        arguments = tool.validate(raw_arguments)
        return PreparedToolCall(call_id=call.id, tool=tool, arguments=arguments)

    @staticmethod
    def execute(prepared: PreparedToolCall) -> str:
        value = prepared.tool.handler(**prepared.arguments)
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)
