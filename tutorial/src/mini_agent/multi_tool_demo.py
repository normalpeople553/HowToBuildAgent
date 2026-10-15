"""Ask DeepSeek to use two independent tools in one task."""

from __future__ import annotations

import os

from .agent import Agent
from .example_tools import build_example_registry
from .real_deepseek import DeepSeekChatModel


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置 DEEPSEEK_API_KEY；不要把 Key 写进源码")
    result = Agent(
        model=DeepSeekChatModel(api_key),
        tools=build_example_registry(),
        instructions=(
            "必须分别调用 get_weather 查询杭州的教学模拟天气，并调用 multiply 计算 19×23；"
            "两个工具都完成后再回答，天气结果必须标明是模拟数据。"
        ),
    ).run("杭州天气如何？顺便计算 19 × 23。")
    print(result.answer)
    print("工具完成顺序：")
    completed_tools = []
    for event in result.trace:
        if event.kind == "tool_finished":
            completed_tools.append(event.data["name"])
            print(f"- {event.data['name']} ({event.data['call_id']})")
    if set(completed_tools) != {"get_weather", "multiply"}:
        raise RuntimeError(f"真实模型没有完成两个指定工具：{completed_tools!r}")


if __name__ == "__main__":
    main()
