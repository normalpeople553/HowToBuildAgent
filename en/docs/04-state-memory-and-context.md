# 04 · Session state, memory and context management

[中文](../../docs/04-状态记忆与上下文管理.md) · [Contents](../../README.en.md)

“Remembering” is not one feature. This chapter separates model context, session state, business state and long-term memory. This is the project's engineering taxonomy, not a vendor-wide standard.

## 1. Four data layers

| Layer | Typical content | Integrity requirement | Suggested storage |
|---|---|---|---|
| Model context | system/user/assistant/tool messages | May be trimmed, but tool protocol must remain complete | Assemble per request |
| Session state | current step, pending confirmation, temporary preferences | Explicit session boundary | Session store or cache |
| Business state | orders, payments, authorization and task state | Source of truth is the business system | Business database |
| Long-term memory | authorized stable preferences or facts | Viewable, editable, deletable and expiring | Separate memory store |

`messages` is context for the current model request, not a business database. A model-generated summary is derived data and must not overwrite original records.

## 2. Assemble context for each turn

Project-recommended order:

```text
System rules and safety boundaries
  + minimum user/session state needed now
  + task-relevant history summary
  + complete tool-call chains that must be preserved
  + current user input
```

Do not send an entire database, all chat history or every raw tool result by default. This increases cost, may exceed the context limit and expands sensitive-data exposure. Check the exact model's context and output budgets in the [Model Manual](https://github.com/normalpeople553/HowToCallLLM/tree/main/models).

## 3. A summary is not the record

Keep source message IDs, summary version and generation method. Re-read permissions, amounts and business status from the source system rather than from a model summary.

Tool chains cannot be compressed arbitrarily: assistant tool calls, matching `tool_call_id` values and tool results must remain paired. Some thinking modes require additional replay fields; follow exact-model documentation. [DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)

## 4. Long-term memory requires a write gate

Do not persist every sentence. Project recommendation: retain information the user explicitly asked to save, stable preferences with later value, and durable facts backed by a business source. Every memory needs user/tenant scope, source, type, expiry and deletion support.

Mark model-inferred attributes as inferences. Do not mix them with explicit user statements or authoritative business facts.

## 5. Concurrency and isolation

Use a version or atomic condition on session updates so concurrent Agent turns cannot overwrite each other. Every query must carry user and tenant boundaries; prompt text saying “do not read another user's data” is not access control. Enforce isolation in storage and tools.

## Checklist

- [ ] Context, session state, business state and long-term memory are stored separately.
- [ ] Critical facts are read from their source of truth, not from summaries.
- [ ] Tool calls and result IDs remain paired.
- [ ] Memory has provenance, expiry, deletion and tenant isolation.
- [ ] Concurrent updates detect conflicts.
- [ ] Context is minimized and screened for sensitive data before model calls.
