"""Run the first complete Agent with DeepSeek V4 Pro."""

from __future__ import annotations

import os

from .agent import Agent
from .example_tools import build_example_registry
from .real_deepseek import DeepSeekChatModel


def build_demo_agent(api_key: str) -> Agent:
    return Agent(
        model=DeepSeekChatModel(api_key),
        tools=build_example_registry(),
        instructions="天气问题必须使用 get_weather，并明确结果是模拟数据。",
    )


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 DEEPSEEK_API_KEY；不要把 Key 写进源码")
    result = build_demo_agent(api_key).run("杭州天气如何？")
    print(result.answer)
    print("\n执行轨迹：")
    for event in result.trace:
        print(f"- {event.kind}: {event.data}")


if __name__ == "__main__":
    main()
