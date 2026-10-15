"""Offline tests for the tutorial agent. No model API request is made."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tutorial" / "src"))

from mini_agent import (
    Agent,
    AgentError,
    ModelReply,
    ScriptedModel,
    Tool,
    ToolCall,
    ToolRegistry,
)
from mini_agent.example_tools import build_example_registry


class TutorialAgentTests(unittest.TestCase):
    def test_complete_tool_loop(self):
        model = ScriptedModel(
            [
                ModelReply(
                    tool_calls=(
                        ToolCall("call_1", "get_weather", '{"city":"杭州"}'),
                    ),
                    finish_reason="tool_calls",
                ),
                ModelReply(content="结果是教学模拟数据。"),
            ]
        )
        result = Agent(
            model=model,
            tools=build_example_registry(),
            instructions="Use the tool.",
        ).run("杭州天气？")

        self.assertEqual(result.answer, "结果是教学模拟数据。")
        self.assertEqual(
            [event.kind for event in result.trace],
            [
                "model_request",
                "model_response",
                "tool_started",
                "tool_finished",
                "model_request",
                "model_response",
                "turn_finished",
            ],
        )
        self.assertEqual(model.requests[1][0][-1]["role"], "tool")
        self.assertEqual(model.requests[1][0][-1]["tool_call_id"], "call_1")

    def test_unknown_tool_is_rejected_before_execution(self):
        model = ScriptedModel(
            [
                ModelReply(
                    tool_calls=(ToolCall("call_1", "delete_everything", "{}"),),
                    finish_reason="tool_calls",
                )
            ]
        )
        agent = Agent(
            model=model,
            tools=build_example_registry(),
            instructions="Use registered tools only.",
        )
        with self.assertRaisesRegex(AgentError, "未注册"):
            agent.run("do it")

    def test_extra_argument_is_rejected(self):
        model = ScriptedModel(
            [
                ModelReply(
                    tool_calls=(
                        ToolCall(
                            "call_1",
                            "get_weather",
                            '{"city":"杭州","extra":true}',
                        ),
                    ),
                    finish_reason="tool_calls",
                )
            ]
        )
        agent = Agent(
            model=model,
            tools=build_example_registry(),
            instructions="Use registered tools only.",
        )
        with self.assertRaisesRegex(AgentError, "只接受 city"):
            agent.run("杭州天气？")

    def test_multiple_tools_in_one_batch(self):
        model = ScriptedModel(
            [
                ModelReply(
                    tool_calls=(
                        ToolCall("weather", "get_weather", '{"city":"杭州"}'),
                        ToolCall("math", "multiply", '{"a":19,"b":23}'),
                    ),
                    finish_reason="tool_calls",
                ),
                ModelReply(content="完成。"),
            ]
        )
        result = Agent(
            model=model,
            tools=build_example_registry(),
            instructions="Use registered tools only.",
        ).run("查天气并计算")
        second_request = model.requests[1][0]
        tool_messages = [item for item in second_request if item["role"] == "tool"]
        self.assertEqual(
            [item["tool_call_id"] for item in tool_messages], ["weather", "math"]
        )
        self.assertEqual(result.answer, "完成。")

    def test_duplicate_call_id_is_rejected(self):
        model = ScriptedModel(
            [
                ModelReply(
                    tool_calls=(
                        ToolCall("same", "get_weather", '{"city":"杭州"}'),
                        ToolCall("same", "get_weather", '{"city":"北京"}'),
                    ),
                    finish_reason="tool_calls",
                )
            ]
        )
        agent = Agent(
            model=model,
            tools=build_example_registry(),
            instructions="Use registered tools only.",
        )
        with self.assertRaisesRegex(AgentError, "ID 重复"):
            agent.run("compare")

    def test_last_allowed_turn_does_not_execute_another_tool(self):
        model = ScriptedModel(
            [
                ModelReply(
                    tool_calls=(
                        ToolCall("call_1", "get_weather", '{"city":"杭州"}'),
                    ),
                    finish_reason="tool_calls",
                )
            ]
        )
        agent = Agent(
            model=model,
            tools=build_example_registry(),
            instructions="Use the tool.",
            max_model_turns=1,
        )
        with self.assertRaisesRegex(AgentError, "调用上限"):
            agent.run("杭州天气？")

    def test_side_effecting_tool_is_denied_by_default(self):
        executed = []
        registry = ToolRegistry()
        registry.register(
            Tool(
                name="save_note",
                description="Save a note.",
                parameters={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                    "additionalProperties": False,
                },
                handler=lambda text: executed.append(text) or "saved",
                validate=lambda arguments: arguments,
                requires_approval=True,
            )
        )
        model = ScriptedModel(
            [
                ModelReply(
                    tool_calls=(
                        ToolCall("save_1", "save_note", '{"text":"hello"}'),
                    ),
                    finish_reason="tool_calls",
                )
            ]
        )
        agent = Agent(model=model, tools=registry, instructions="Save the note.")
        with self.assertRaisesRegex(AgentError, "未批准"):
            agent.run("save hello")
        self.assertEqual(executed, [])


if __name__ == "__main__":
    unittest.main()
