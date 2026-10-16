"""A deliberately small but bounded model-tool loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .approvals import ApprovalPolicy, DenyAll
from .models import Message, ModelClient, ModelReply
from .tools import PreparedToolCall, ToolRegistry
from .tracing import TraceEvent, TraceRecorder


class AgentError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentResult:
    answer: str
    messages: tuple[Message, ...]
    trace: tuple[TraceEvent, ...]


class Agent:
    def __init__(
        self,
        *,
        model: ModelClient,
        tools: ToolRegistry,
        instructions: str,
        max_model_turns: int = 6,
        max_tool_result_chars: int = 4_000,
        approvals: ApprovalPolicy | None = None,
    ) -> None:
        if max_model_turns < 1:
            raise ValueError("max_model_turns 必须至少为 1")
        if max_tool_result_chars < 1:
            raise ValueError("max_tool_result_chars 必须至少为 1")
        self.model = model
        self.tools = tools
        self.instructions = instructions
        self.max_model_turns = max_model_turns
        self.max_tool_result_chars = max_tool_result_chars
        self.approvals = approvals or DenyAll()

    def run(self, user_input: str) -> AgentResult:
        if not user_input.strip():
            raise ValueError("用户输入不能为空")

        messages: list[Message] = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": user_input.strip()},
        ]
        trace = TraceRecorder()
        used_call_ids: set[str] = set()

        for turn_index in range(self.max_model_turns):
            trace.add("model_request", turn=turn_index + 1)
            reply = self.model.complete(messages, self.tools.public_specs())
            trace.add(
                "model_response",
                turn=turn_index + 1,
                finish_reason=reply.finish_reason,
                tool_count=len(reply.tool_calls),
            )

            if reply.tool_calls:
                if reply.finish_reason != "tool_calls":
                    raise AgentError("模型返回了工具调用，但结束原因不是 tool_calls")
                if turn_index == self.max_model_turns - 1:
                    raise AgentError("达到模型调用上限，未再执行工具")
                prepared = self._prepare_batch(reply, used_call_ids)
                messages.append(self._assistant_tool_message(reply))
                for item in prepared:
                    self._check_approval(item, trace)
                    trace.add("tool_started", name=item.tool.name, call_id=item.call_id)
                    output = self.tools.execute(item)
                    if len(output) > self.max_tool_result_chars:
                        output = output[: self.max_tool_result_chars] + "…[已截断]"
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": item.call_id,
                            "content": output,
                        }
                    )
                    trace.add(
                        "tool_finished",
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
            messages.append({"role": "assistant", "content": answer})
            trace.add("turn_finished", answer_chars=len(answer))
            return AgentResult(answer, tuple(messages), tuple(trace.events))

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
        trace.add("tool_rejected", name=prepared.tool.name, call_id=prepared.call_id)
        raise AgentError(f"用户未批准工具：{prepared.tool.name}")

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
