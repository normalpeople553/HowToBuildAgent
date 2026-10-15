"""Connect the tutorial loop to DeepSeek V4 Pro through Chat Completions.

Official protocol sources:
- https://api-docs.deepseek.com/guides/tool_calls/
- https://api-docs.deepseek.com/api/create-chat-completion/
"""

from __future__ import annotations

import os
from typing import Sequence

from .agent import Agent
from .example_tools import build_example_registry
from .models import Message, ModelReply, ToolCall, ToolSpec


class DeepSeekChatModel:
    def __init__(self, api_key: str, model: str = "deepseek-v4-pro") -> None:
        from openai import OpenAI

        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=120,
        )
        self._model = model

    def complete(
        self, messages: Sequence[Message], tools: Sequence[ToolSpec]
    ) -> ModelReply:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=list(messages),
            tools=list(tools),
            tool_choice="auto",
            extra_body={"thinking": {"type": "disabled"}},
        )
        if not response.choices:
            raise RuntimeError("DeepSeek 响应没有 choices")
        choice = response.choices[0]
        calls = tuple(
            ToolCall(
                id=call.id,
                name=call.function.name,
                arguments=call.function.arguments,
            )
            for call in (choice.message.tool_calls or [])
            if call.type == "function"
        )
        return ModelReply(
            content=choice.message.content,
            tool_calls=calls,
            finish_reason=choice.finish_reason or "unknown",
        )


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 DEEPSEEK_API_KEY；不要把 Key 写进源码")
    agent = Agent(
        model=DeepSeekChatModel(api_key),
        tools=build_example_registry(),
        instructions="天气问题必须使用 get_weather，并明确结果是模拟数据。",
    )
    result = agent.run("杭州天气如何？")
    print(result.answer)


if __name__ == "__main__":
    main()
