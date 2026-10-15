# 03 · Multiple tools, routing and loop control

[中文](../../docs/03-多工具路由与循环控制.md) · [Contents](../../README.en.md)

One tool may fit in an `if`; several tools need an explicit registry, router, executor and loop budget. Verify tool fields, parallel-call behavior and `tool_choice` against the exact model. [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/) · [Model Manual executable tool example](https://github.com/normalpeople553/HowToCallLLM/blob/main/models/deepseek/deepseek-flash/examples/05_tool_calling.py)

## 1. Four components

| Component | Responsibility | Must not do |
|---|---|---|
| Registry | Name, description, schema, risk class and handler | Let the model register arbitrary functions |
| Router | Map allowed names to local handlers | `eval` model text |
| Executor | Validate, authorize, time out, execute and normalize results | Bypass business authorization |
| Loop controller | Preserve messages and IDs, enforce turns and stops | Run an unlimited `while True` |

The model proposes a tool name and arguments. The application owns the mapping to real code.

## 2. Tool descriptions are a routing interface

Project recommendation: give each tool one stable action, state when it should and should not be used, and expose only the smallest required arguments. Merge overlapping tools or separate sub-actions with a constrained enum.

A visible tool is not automatically authorized. Recheck user and resource authorization for every execution. This follows OWASP's guidance to minimize functionality, permissions and autonomy for [Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/).

## 3. A bounded loop

This is control-flow pseudocode, not a provider API example:

```text
Set max_turns, max_tool_calls, deadline and cost_budget
Repeat:
  stop if any budget is exceeded
  call the model
  if final text: verify termination and return
  if tool calls:
    validate the complete batch
    choose serial or parallel execution from dependencies and side effects
    execute and preserve each tool_call_id result
    continue
  otherwise: stop with an error
```

Calls in one model response are not automatically safe to parallelize. Parallelize independent reads; serialize dependencies, shared locks and side effects. This is an application scheduling policy, not a protocol guarantee.

## 4. Idempotency and retries

Retry a write only when the previous attempt is known not to have taken effect or the downstream system supports an idempotency key. Use a stable business request ID and record accepted, executed and result-delivered states separately. Model text saying “success” is not proof of a business outcome.

## 5. Stop reasons

Distinguish normal completion, user cancellation, clarification required, confirmation required, argument error, tool error, timeout, turn limit, cost limit and safety block. Keep user-facing text separate from machine-readable status so failures can be tested and monitored.

## Checklist

- [ ] Tool names map only to a static allowlist.
- [ ] The whole batch is validated before any call executes.
- [ ] Turns, tool calls, time and cost all have limits.
- [ ] Side-effect retries use idempotency or deduplication.
- [ ] Parallel execution is restricted to independent safe calls.
- [ ] Stop reasons are machine-readable and observable.
