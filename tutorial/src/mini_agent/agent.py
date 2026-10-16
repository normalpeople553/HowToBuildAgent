"""Compatibility facade over the Thread/Turn Agent kernel."""

from __future__ import annotations

from dataclasses import dataclass

from .approvals import ApprovalPolicy
from .core import AgentError
from .core import AgentKernel
from .core import AgentThread
from .core import KernelEvent
from .core import ThreadItem
from .models import Message, ModelClient
from .tools import ToolRegistry
from .tracing import TraceEvent


@dataclass(frozen=True)
class AgentResult:
    answer: str
    messages: tuple[Message, ...]
    trace: tuple[TraceEvent, ...]
    thread_id: str
    turn_id: str
    items: tuple[ThreadItem, ...]
    events: tuple[KernelEvent, ...]


class Agent:
    """Small public API that keeps the original one-shot `run()` entrypoint."""

    def __init__(
        self,
        *,
        model: ModelClient,
        tools: ToolRegistry,
        instructions: str,
        max_model_steps: int | None = None,
        max_model_turns: int | None = None,
        max_tool_result_chars: int = 4_000,
        approvals: ApprovalPolicy | None = None,
    ) -> None:
        self.kernel = AgentKernel(
            model=model,
            tools=tools,
            instructions=instructions,
            max_model_steps=max_model_steps,
            max_model_turns=max_model_turns,
            max_tool_result_chars=max_tool_result_chars,
            approvals=approvals,
        )

    def create_thread(self) -> AgentThread:
        """Create a reusable conversation for multiple user turns."""

        return self.kernel.create_thread()

    def run_turn(self, thread_id: str, user_input: str) -> AgentResult:
        """Run one task inside an existing thread."""

        turn = self.kernel.start_turn(thread_id, user_input)
        if turn.answer is None:
            raise AgentError("Turn 已完成但没有答案")
        thread = self.kernel.get_thread(thread_id)
        return AgentResult(
            answer=turn.answer,
            messages=tuple(thread.messages),
            trace=tuple(turn.trace),
            thread_id=thread.id,
            turn_id=turn.id,
            items=tuple(turn.items),
            events=self.kernel.events_for(thread.id, turn.id),
        )

    def run(self, user_input: str) -> AgentResult:
        """Create a fresh thread and run one turn, preserving the old tutorial API."""

        thread = self.create_thread()
        return self.run_turn(thread.id, user_input)
