# 01 · From a Model Call to Your First Agent

[中文](../../docs/01-从模型调用到第一个Agent.md) · [Contents](../../README.en.md) · [Previous](00-read-this-first.md)

This chapter takes apart the Mini Agent you just ran. The goal is to understand the responsibilities hidden by larger frameworks.

## The five parts

| Part | Tutorial code | Responsibility |
|---|---|---|
| Model adapter | [`real_deepseek.py`](../../tutorial/src/mini_agent/real_deepseek.py) | Call DeepSeek and return final text or proposed tool calls |
| Tool registry | [`tools.py`](../../tutorial/src/mini_agent/tools.py) | Bind public descriptions and schemas to local handlers |
| Kernel and loop | [`core.py`](../../tutorial/src/mini_agent/core.py) | Own Thread/Turn state, ask, validate, execute, return results, and stop |
| State | `AgentThread`, `Turn`, and `used_call_ids` | Preserve multi-turn history, task state, and call IDs |
| Boundaries | budgets, validation, and approval | Prevent unbounded or unauthorized execution |

OpenAI's agent overview separates model configuration, tools, state, and execution environments; when you build directly on model responses, your application owns the loop, history, and local tool execution. [Agents](https://developers.openai.com/api/docs/guides/agents)

## Read the real model adapter first

`DeepSeekChatModel.complete(messages, tools)` calls the online DeepSeek API and converts the provider response into a small `ModelReply`: content, tool calls, and a finish reason. It explicitly uses `deepseek-v4-pro`, `https://api.deepseek.com`, automatic tool selection, and non-thinking mode. Verify those fields in the current [DeepSeek Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/).

The tutorial starts with this real adapter. `ScriptedModel` exists only so unit tests can reproduce specific failures without spending API tokens.

## A tool description is not the function

[`example_tools.py`](../../tutorial/src/mini_agent/example_tools.py) separates the Python handler, application validation, and the model-visible name, description, and JSON Schema. `required` declares mandatory properties and `additionalProperties: false` rejects undeclared properties. [JSON Schema objects](https://json-schema.org/understanding-json-schema/reference/object)

Only explicitly registered handlers can execute. Model-generated names and arguments are untrusted input; the application must never `eval` them or dynamically search for matching local functions.

## Follow the seven trace events

Run `mini-agent-demo` and compare its output with `AgentKernel.start_turn()`. `Agent.run()` remains the one-shot compatibility entrypoint:

1. Send current messages and public tool specs to the model.
2. Receive final text or one or more proposed tool calls.
3. Validate the entire batch before executing any call.
4. Append the assistant message containing the tool calls.
5. Execute approved handlers and append results using matching call IDs.
6. Ask the model again with the expanded history.
7. Return only after a normal stop with non-empty final text.

Function calling is a multi-step application conversation, not remote execution performed by the model. [OpenAI Function calling](https://developers.openai.com/api/docs/guides/function-calling) DeepSeek likewise requires the assistant tool-call message and matching tool result before the next request. [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)

The final allowed model turn cannot start another tool execution: there would be no remaining model call to consume the result and complete the task.

## Reproduce failures with fixed tests

Open [`tests/test_tutorial_agent.py`](../../tests/test_tutorial_agent.py). Its fixed responses cover an unknown tool, an undeclared argument, duplicate IDs, the final-turn boundary, and denied side effects.

Then run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Keep the roles clear

`mini-agent-demo` and `mini-agent-multi` use real DeepSeek and may incur charges. `ScriptedModel` is only a unit-test double: it is neither a local model nor the tutorial default. Current model identities, provider behavior, pricing links, and separately verified call examples belong in the [Model Manual](https://github.com/normalpeople553/HowToCallLLM/tree/main/models/deepseek).

Continue with [02 · Structured Output and Validation](02-structured-output-and-validation.md).

After Lessons 02–08, [09 · Thread and Turn](09-thread-and-turn-kernel.md) explains the kernel structure in full.
