"""Run the first complete agent without a network request or API key."""

from __future__ import annotations

from .agent import Agent
from .example_tools import build_example_registry
from .models import ModelReply, ScriptedModel, ToolCall


def build_demo_agent() -> Agent:
    model = ScriptedModel(
        [
            ModelReply(
                tool_calls=(
                    ToolCall(
                        id="call_demo_1",
                        name="get_weather",
                        arguments='{"city":"杭州"}',
                    ),
                ),
                finish_reason="tool_calls",
            ),
            ModelReply(content="杭州：晴。这是教学模拟数据，不是实时天气。"),
        ]
    )
    return Agent(
        model=model,
        tools=build_example_registry(),
        instructions="天气问题必须使用 get_weather，并明确结果是模拟数据。",
    )


def main() -> None:
    result = build_demo_agent().run("杭州天气如何？")
    print(result.answer)
    print("\n执行轨迹：")
    for event in result.trace:
        print(f"- {event.kind}: {event.data}")


if __name__ == "__main__":
    main()
