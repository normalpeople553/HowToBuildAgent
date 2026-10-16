# 09 · Thread and Turn: From a Loop to a Kernel

[中文](../../docs/09-Thread与Turn内核.md) · [Contents](../../README.en.md) · [Previous](08-security-confirmation-and-deployment.md)

This chapter adds a small multi-turn kernel. The following structure is this project's design contract rather than a universal provider API schema.

| Layer | Lifetime | Python type | Responsibility |
|---|---|---|---|
| Thread | Multiple user tasks | `AgentThread` | Completed model-visible history, Turns, and active state |
| Turn | One user submission | `Turn` | One task from start to completion, failure, or interruption |
| Item | One fact inside a Turn | `ThreadItem` | User input, model response, tool call, tool result, or final answer |
| Event | A lifecycle change | `KernelEvent` | Observation for clients, logs, and tests without owning control flow |

The implementation is [`core.py`](../../tutorial/src/mini_agent/core.py). The original [`Agent`](../../tutorial/src/mini_agent/agent.py) remains a compatibility facade: `run()` creates one Thread and one Turn, while `create_thread()` plus `run_turn()` supports continuing conversations.

One Turn may contain multiple model requests. The kernel calls those requests model steps and bounds them with `max_model_steps`; the old `max_model_turns` name remains only as a compatibility alias.

```text
Thread: idle -> active -> idle
Turn:   in_progress -> completed | failed | interrupted
```

Only one Turn may be active in a Thread. Items answer what happened; Events announce lifecycle changes. Successful messages remain in model-visible Thread history. Failed or interrupted Turns retain Items and Events for diagnosis while their incomplete provider message sequence is rolled back, preventing a later request from inheriting an unmatched tool call.

`interrupt_turn()` is cooperative: the kernel observes it after a blocking model request returns or before the next tool executes. It does not forcibly terminate a blocking SDK or handler.

The v1 kernel is intentionally in-memory and synchronous. It does not yet provide persistence, recovery, streaming, context compaction, branches, queues, MCP, multi-agent orchestration, or automatic event-log redaction.

Run the local suite and inspect [`test_kernel.py`](../../tests/test_kernel.py):

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
