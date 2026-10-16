"""A small Thread/Turn kernel for the tutorial runtime.

The kernel keeps durable conversation structure separate from the model-tool
loop: a Thread owns history, a Turn owns one submitted task, Items describe
what happened, and Events let callers observe lifecycle changes.
"""

from __future__ import annotations

import copy
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .approvals import ApprovalPolicy, DenyAll
from .models import Message, ModelClient, ModelReply
from .tools import PreparedToolCall, ToolRegistry
from .tracing import TraceEvent, TraceRecorder


class AgentError(RuntimeError):
    """Base error raised by the Agent kernel."""


class UnknownThreadError(AgentError):
    """Raised when a caller addresses a thread that does not exist."""


class ThreadBusyError(AgentError):
    """Raised when a caller starts a second turn on an active thread."""


class TurnInterruptedError(AgentError):
    """Raised after cooperative interruption stops a turn."""


class ThreadStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"


class TurnStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class ItemKind(str, Enum):
    USER_MESSAGE = "user_message"
    MODEL_RESPONSE = "model_response"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ASSISTANT_MESSAGE = "assistant_message"
    ERROR = "error"


@dataclass
class ThreadItem:
    id: str
    kind: ItemKind
    data: dict[str, Any]


@dataclass
class Turn:
    id: str
    status: TurnStatus
    items: list[ThreadItem] = field(default_factory=list)
    answer: str | None = None
    error: str | None = None
    trace: list[TraceEvent] = field(default_factory=list)


@dataclass
class AgentThread:
    id: str
    status: ThreadStatus
    messages: list[Message]
    turns: list[Turn] = field(default_factory=list)
    active_turn_id: str | None = None


@dataclass(frozen=True)
class KernelEvent:
    sequence: int
    kind: str
    thread_id: str
    turn_id: str | None = None
    item_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


class AgentKernel:
    """Own threads and execute one bounded model-tool loop per turn."""

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
        if (
            max_model_steps is not None
            and max_model_turns is not None
            and max_model_steps != max_model_turns
        ):
            raise ValueError("max_model_steps 与兼容参数 max_model_turns 不能冲突")
        resolved_model_steps = (
            max_model_steps
            if max_model_steps is not None
            else max_model_turns if max_model_turns is not None else 6
        )
        if resolved_model_steps < 1:
            raise ValueError("max_model_steps 必须至少为 1")
        if max_tool_result_chars < 1:
            raise ValueError("max_tool_result_chars 必须至少为 1")
        self.model = model
        self.tools = tools
        self.instructions = instructions
        self.max_model_steps = resolved_model_steps
        self.max_tool_result_chars = max_tool_result_chars
        self.approvals = approvals or DenyAll()
        self._threads: dict[str, AgentThread] = {}
        self._events: list[KernelEvent] = []
        self._interrupt_requests: set[tuple[str, str]] = set()
        self._lock = threading.RLock()

    def create_thread(self) -> AgentThread:
        thread = AgentThread(
            id=self._new_id("thread"),
            status=ThreadStatus.IDLE,
            messages=[{"role": "system", "content": self.instructions}],
        )
        with self._lock:
            self._threads[thread.id] = thread
            self._emit("thread_created", thread.id)
            return copy.deepcopy(thread)

    def get_thread(self, thread_id: str) -> AgentThread:
        with self._lock:
            return copy.deepcopy(self._require_thread(thread_id))

    def list_threads(self) -> tuple[AgentThread, ...]:
        with self._lock:
            return tuple(copy.deepcopy(thread) for thread in self._threads.values())

    def events_for(
        self, thread_id: str, turn_id: str | None = None
    ) -> tuple[KernelEvent, ...]:
        with self._lock:
            return tuple(
                copy.deepcopy(event)
                for event in self._events
                if event.thread_id == thread_id
                and (turn_id is None or event.turn_id == turn_id)
            )

    def start_turn(self, thread_id: str, user_input: str) -> Turn:
        user_input = user_input.strip()
        if not user_input:
            raise ValueError("用户输入不能为空")

        with self._lock:
            thread = self._require_thread(thread_id)
            if thread.active_turn_id is not None:
                raise ThreadBusyError(
                    f"线程已有运行中的 Turn：{thread.active_turn_id}"
                )
            turn = Turn(id=self._new_id("turn"), status=TurnStatus.IN_PROGRESS)
            thread.turns.append(turn)
            thread.status = ThreadStatus.ACTIVE
            thread.active_turn_id = turn.id
            history_checkpoint = len(thread.messages)
            thread.messages.append({"role": "user", "content": user_input})
            self._emit("turn_started", thread.id, turn.id)
            self._add_item(
                thread,
                turn,
                ItemKind.USER_MESSAGE,
                {"content": user_input},
            )

        trace = TraceRecorder()
        try:
            answer = self._run_model_loop(thread, turn, trace)
        except TurnInterruptedError as exc:
            with self._lock:
                del thread.messages[history_checkpoint:]
                turn.status = TurnStatus.INTERRUPTED
                turn.error = str(exc)
                turn.trace = list(trace.events)
                self._add_item(
                    thread, turn, ItemKind.ERROR, {"message": str(exc)}
                )
                self._finish_thread_turn(thread, turn, "turn_interrupted")
            raise
        except Exception as exc:
            error = exc if isinstance(exc, AgentError) else AgentError(str(exc))
            with self._lock:
                # Keep audit Items but discard the incomplete provider message
                # sequence so a later turn never resumes malformed history.
                del thread.messages[history_checkpoint:]
                turn.status = TurnStatus.FAILED
                turn.error = str(error)
                turn.trace = list(trace.events)
                self._add_item(
                    thread, turn, ItemKind.ERROR, {"message": str(error)}
                )
                self._finish_thread_turn(thread, turn, "turn_failed")
            if error is exc:
                raise
            raise error from exc

        with self._lock:
            turn.status = TurnStatus.COMPLETED
            turn.answer = answer
            turn.trace = list(trace.events)
            self._finish_thread_turn(
                thread,
                turn,
                "turn_completed",
                answer_chars=len(answer),
            )
            return copy.deepcopy(turn)

    def interrupt_turn(self, thread_id: str, turn_id: str) -> None:
        """Request cooperative interruption between model and tool steps."""

        with self._lock:
            thread = self._require_thread(thread_id)
            if thread.active_turn_id != turn_id:
                raise AgentError("目标 Turn 当前没有运行")
            self._interrupt_requests.add((thread_id, turn_id))
            self._emit("turn_interrupt_requested", thread_id, turn_id)

    def _run_model_loop(
        self, thread: AgentThread, turn: Turn, trace: TraceRecorder
    ) -> str:
        used_call_ids: set[str] = set()
        for model_step_index in range(self.max_model_steps):
            self._raise_if_interrupted(thread.id, turn.id)
            trace.add("model_request", turn=model_step_index + 1)
            reply = self.model.complete(
                copy.deepcopy(thread.messages), self.tools.public_specs()
            )
            self._raise_if_interrupted(thread.id, turn.id)
            trace.add(
                "model_response",
                turn=model_step_index + 1,
                finish_reason=reply.finish_reason,
                tool_count=len(reply.tool_calls),
            )
            with self._lock:
                self._add_item(
                    thread,
                    turn,
                    ItemKind.MODEL_RESPONSE,
                    {
                        "content": reply.content,
                        "finish_reason": reply.finish_reason,
                        "tool_count": len(reply.tool_calls),
                    },
                )

            if reply.tool_calls:
                if reply.finish_reason != "tool_calls":
                    raise AgentError("模型返回了工具调用，但结束原因不是 tool_calls")
                if model_step_index == self.max_model_steps - 1:
                    raise AgentError("达到模型调用上限，未再执行工具")
                prepared = self._prepare_batch(reply, used_call_ids)
                with self._lock:
                    thread.messages.append(self._assistant_tool_message(reply))
                for item in prepared:
                    self._raise_if_interrupted(thread.id, turn.id)
                    with self._lock:
                        tool_item = self._add_item(
                            thread,
                            turn,
                            ItemKind.TOOL_CALL,
                            {
                                "call_id": item.call_id,
                                "name": item.tool.name,
                                "arguments": copy.deepcopy(item.arguments),
                            },
                        )
                    self._check_approval(item, trace)
                    trace.add(
                        "tool_started", name=item.tool.name, call_id=item.call_id
                    )
                    self._emit(
                        "tool_started",
                        thread.id,
                        turn.id,
                        tool_item.id,
                        name=item.tool.name,
                        call_id=item.call_id,
                    )
                    output = self.tools.execute(item)
                    if len(output) > self.max_tool_result_chars:
                        output = output[: self.max_tool_result_chars] + "…[已截断]"
                    with self._lock:
                        thread.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": item.call_id,
                                "content": output,
                            }
                        )
                        result_item = self._add_item(
                            thread,
                            turn,
                            ItemKind.TOOL_RESULT,
                            {
                                "call_id": item.call_id,
                                "name": item.tool.name,
                                "output": output,
                            },
                        )
                    trace.add(
                        "tool_finished",
                        name=item.tool.name,
                        call_id=item.call_id,
                        output_chars=len(output),
                    )
                    self._emit(
                        "tool_finished",
                        thread.id,
                        turn.id,
                        result_item.id,
                        name=item.tool.name,
                        call_id=item.call_id,
                        output_chars=len(output),
                    )
                continue

            if reply.finish_reason != "stop":
                raise AgentError(f"模型没有正常结束：{reply.finish_reason!r}")
            if not isinstance(reply.content, str) or not reply.content.strip():
                raise AgentError("模型正常结束但没有最终正文")
            answer = reply.content.strip()
            with self._lock:
                thread.messages.append({"role": "assistant", "content": answer})
                self._add_item(
                    thread,
                    turn,
                    ItemKind.ASSISTANT_MESSAGE,
                    {"content": answer},
                )
            trace.add("turn_finished", answer_chars=len(answer))
            return answer

        raise AgentError("达到模型调用上限，Agent 仍未完成")

    def _prepare_batch(
        self, reply: ModelReply, used_call_ids: set[str]
    ) -> list[PreparedToolCall]:
        prepared: list[PreparedToolCall] = []
        batch_ids: set[str] = set()
        for call in reply.tool_calls:
            if call.id in used_call_ids or call.id in batch_ids:
                raise AgentError(f"工具调用 ID 重复：{call.id!r}")
            try:
                item = self.tools.prepare(call)
            except ValueError as exc:
                raise AgentError(str(exc)) from exc
            prepared.append(item)
            batch_ids.add(call.id)
        used_call_ids.update(batch_ids)
        return prepared

    def _check_approval(
        self, prepared: PreparedToolCall, trace: TraceRecorder
    ) -> None:
        if not prepared.tool.requires_approval:
            return
        if self.approvals.allow(prepared.tool.name, prepared.arguments):
            trace.add(
                "tool_approved", name=prepared.tool.name, call_id=prepared.call_id
            )
            return
        trace.add(
            "tool_rejected", name=prepared.tool.name, call_id=prepared.call_id
        )
        raise AgentError(f"用户未批准工具：{prepared.tool.name}")

    def _raise_if_interrupted(self, thread_id: str, turn_id: str) -> None:
        with self._lock:
            key = (thread_id, turn_id)
            if key in self._interrupt_requests:
                self._interrupt_requests.remove(key)
                raise TurnInterruptedError("Turn 已被中断")

    def _add_item(
        self,
        thread: AgentThread,
        turn: Turn,
        kind: ItemKind,
        data: dict[str, Any],
    ) -> ThreadItem:
        item = ThreadItem(id=self._new_id("item"), kind=kind, data=data)
        turn.items.append(item)
        self._emit(
            "item_added",
            thread.id,
            turn.id,
            item.id,
            item_kind=kind.value,
        )
        return item

    def _finish_thread_turn(
        self, thread: AgentThread, turn: Turn, event_kind: str, **data: Any
    ) -> None:
        thread.active_turn_id = None
        thread.status = ThreadStatus.IDLE
        self._interrupt_requests.discard((thread.id, turn.id))
        self._emit(event_kind, thread.id, turn.id, **data)

    def _require_thread(self, thread_id: str) -> AgentThread:
        thread = self._threads.get(thread_id)
        if thread is None:
            raise UnknownThreadError(f"线程不存在：{thread_id}")
        return thread

    def _emit(
        self,
        kind: str,
        thread_id: str,
        turn_id: str | None = None,
        item_id: str | None = None,
        **data: Any,
    ) -> None:
        with self._lock:
            self._events.append(
                KernelEvent(
                    sequence=len(self._events) + 1,
                    kind=kind,
                    thread_id=thread_id,
                    turn_id=turn_id,
                    item_id=item_id,
                    data=copy.deepcopy(data),
                )
            )

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"

    @staticmethod
    def _assistant_tool_message(reply: ModelReply) -> Message:
        return {
            "role": "assistant",
            "content": reply.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                }
                for call in reply.tool_calls
            ],
        }
