"""Thread/Turn kernel tests. No provider API request is made."""

from pathlib import Path
import sys
import threading
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tutorial" / "src"))

from mini_agent import (
    Agent,
    AgentError,
    AgentKernel,
    ItemKind,
    ModelReply,
    ScriptedModel,
    ThreadBusyError,
    ThreadStatus,
    ToolCall,
    TurnInterruptedError,
    TurnStatus,
    UnknownThreadError,
)
from mini_agent.example_tools import build_example_registry


class KernelTests(unittest.TestCase):
    def test_turn_lifecycle_records_items_and_events(self):
        kernel = AgentKernel(
            model=ScriptedModel(
                [
                    ModelReply(
                        tool_calls=(
                            ToolCall("weather_1", "get_weather", '{"city":"杭州"}'),
                        ),
                        finish_reason="tool_calls",
                    ),
                    ModelReply(content="结果来自教学模拟工具。"),
                ]
            ),
            tools=build_example_registry(),
            instructions="Use tools.",
        )

        thread = kernel.create_thread()
        turn = kernel.start_turn(thread.id, "杭州天气？")
        snapshot = kernel.get_thread(thread.id)

        self.assertEqual(turn.status, TurnStatus.COMPLETED)
        self.assertEqual(snapshot.status, ThreadStatus.IDLE)
        self.assertIsNone(snapshot.active_turn_id)
        self.assertEqual(
            [item.kind for item in turn.items],
            [
                ItemKind.USER_MESSAGE,
                ItemKind.MODEL_RESPONSE,
                ItemKind.TOOL_CALL,
                ItemKind.TOOL_RESULT,
                ItemKind.MODEL_RESPONSE,
                ItemKind.ASSISTANT_MESSAGE,
            ],
        )
        events = kernel.events_for(thread.id, turn.id)
        self.assertEqual(events[0].kind, "turn_started")
        self.assertEqual(events[-1].kind, "turn_completed")
        self.assertTrue(all(event.turn_id == turn.id for event in events))

    def test_one_thread_preserves_only_completed_turn_history(self):
        model = ScriptedModel(
            [ModelReply(content="第一轮完成。"), ModelReply(content="第二轮完成。")]
        )
        agent = Agent(
            model=model,
            tools=build_example_registry(),
            instructions="Answer briefly.",
        )
        thread = agent.create_thread()

        first = agent.run_turn(thread.id, "第一问")
        second = agent.run_turn(thread.id, "第二问")

        self.assertNotEqual(first.turn_id, second.turn_id)
        self.assertEqual(
            [message["role"] for message in model.requests[1][0]],
            ["system", "user", "assistant", "user"],
        )
        snapshot = agent.kernel.get_thread(thread.id)
        self.assertEqual(len(snapshot.turns), 2)
        self.assertTrue(
            all(turn.status == TurnStatus.COMPLETED for turn in snapshot.turns)
        )

    def test_failed_turn_is_audited_but_provider_history_rolls_back(self):
        kernel = AgentKernel(
            model=ScriptedModel(
                [
                    ModelReply(
                        tool_calls=(ToolCall("bad", "not_registered", "{}"),),
                        finish_reason="tool_calls",
                    )
                ]
            ),
            tools=build_example_registry(),
            instructions="Use tools.",
        )
        thread = kernel.create_thread()

        with self.assertRaisesRegex(AgentError, "未注册"):
            kernel.start_turn(thread.id, "执行未知工具")

        snapshot = kernel.get_thread(thread.id)
        self.assertEqual(snapshot.status, ThreadStatus.IDLE)
        self.assertEqual([message["role"] for message in snapshot.messages], ["system"])
        self.assertEqual(snapshot.turns[0].status, TurnStatus.FAILED)
        self.assertEqual(snapshot.turns[0].items[-1].kind, ItemKind.ERROR)
        self.assertEqual(
            kernel.events_for(thread.id, snapshot.turns[0].id)[-1].kind,
            "turn_failed",
        )

    def test_thread_snapshots_cannot_mutate_kernel_state(self):
        kernel = AgentKernel(
            model=ScriptedModel([]),
            tools=build_example_registry(),
            instructions="Stay safe.",
        )
        snapshot = kernel.create_thread()
        snapshot.messages.append({"role": "user", "content": "outside mutation"})
        events = list(kernel.events_for(snapshot.id))
        events[0].data["outside"] = True

        stored = kernel.get_thread(snapshot.id)
        self.assertEqual([message["role"] for message in stored.messages], ["system"])
        self.assertNotIn("outside", kernel.events_for(snapshot.id)[0].data)

    def test_unknown_thread_is_rejected(self):
        kernel = AgentKernel(
            model=ScriptedModel([]),
            tools=build_example_registry(),
            instructions="Stay safe.",
        )
        with self.assertRaises(UnknownThreadError):
            kernel.start_turn("missing", "hello")

    def test_legacy_model_turn_budget_alias_cannot_conflict(self):
        with self.assertRaisesRegex(ValueError, "不能冲突"):
            AgentKernel(
                model=ScriptedModel([]),
                tools=build_example_registry(),
                instructions="Stay safe.",
                max_model_steps=2,
                max_model_turns=3,
            )

    def test_interrupt_requested_during_model_call_stops_turn(self):
        class BlockingModel:
            def __init__(self):
                self.started = threading.Event()
                self.release = threading.Event()

            def complete(self, messages, tools):
                self.started.set()
                if not self.release.wait(timeout=2):
                    raise RuntimeError("test release timed out")
                return ModelReply(content="should not be committed")

        model = BlockingModel()
        kernel = AgentKernel(
            model=model,
            tools=build_example_registry(),
            instructions="Wait.",
        )
        thread = kernel.create_thread()
        errors = []

        def run_turn():
            try:
                kernel.start_turn(thread.id, "wait")
            except Exception as exc:
                errors.append(exc)

        worker = threading.Thread(target=run_turn)
        worker.start()
        self.assertTrue(model.started.wait(timeout=2))
        active = kernel.get_thread(thread.id)
        with self.assertRaises(ThreadBusyError):
            kernel.start_turn(thread.id, "second turn")
        kernel.interrupt_turn(thread.id, active.active_turn_id)
        model.release.set()
        worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], TurnInterruptedError)
        snapshot = kernel.get_thread(thread.id)
        self.assertEqual(snapshot.turns[0].status, TurnStatus.INTERRUPTED)
        self.assertEqual([message["role"] for message in snapshot.messages], ["system"])


if __name__ == "__main__":
    unittest.main()
