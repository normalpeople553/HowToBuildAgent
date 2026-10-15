"""Model-facing types plus a deterministic test double."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence


Message = dict[str, Any]
ToolSpec = dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    """One tool request proposed by a model."""

    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class ModelReply:
    """The small subset of a model response needed by our agent loop."""

    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    finish_reason: str = "stop"


class ModelClient(Protocol):
    """Anything that can turn history and tool specs into the model's next step."""

    def complete(
        self, messages: Sequence[Message], tools: Sequence[ToolSpec]
    ) -> ModelReply:
        ...


class ScriptedModel:
    """Return predefined replies for unit tests without replacing the real tutorial model."""

    def __init__(self, replies: Sequence[ModelReply]) -> None:
        self._replies = list(replies)
        self.requests: list[tuple[list[Message], list[ToolSpec]]] = []

    def complete(
        self, messages: Sequence[Message], tools: Sequence[ToolSpec]
    ) -> ModelReply:
        self.requests.append((list(messages), list(tools)))
        if not self._replies:
            raise RuntimeError("脚本模型没有下一条回复；请检查测试轨迹")
        return self._replies.pop(0)
