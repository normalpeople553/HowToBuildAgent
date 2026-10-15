"""Run two independent tools returned in one model response."""

from __future__ import annotations

from .agent import Agent
from .example_tools import build_example_registry
from .models import ModelReply, ScriptedModel, ToolCall


def main() -> None:
    model = ScriptedModel(
        [
            ModelReply(
                tool_calls=(
                    ToolCall("call_weather", "get_weather", '{"city":"杭州"}'),
                    ToolCall("call_math", "multiply", '{"a":19,"b":23}'),
                ),
                finish_reason="tool_calls",
            ),
            ModelReply(
                content="杭州天气为晴（模拟数据）；19 × 23 = 437。"
            ),
        ]
    )
    result = Agent(
        model=model,
        tools=build_example_registry(),
        instructions="按需使用已注册工具；天气结果必须标明是模拟数据。",
    ).run("杭州天气如何？顺便计算 19 × 23。")
    print(result.answer)
    print("工具完成顺序：")
    for event in result.trace:
        if event.kind == "tool_finished":
            print(f"- {event.data['name']} ({event.data['call_id']})")


if __name__ == "__main__":
    main()
