# 01 · From a Model Call to Your First Agent

[中文](../../docs/01-从模型调用到第一个Agent.md) · [Contents](../../README.en.md) · [Previous](00-read-this-first.md)

This chapter takes apart the Mini Agent you just ran. The goal is to understand the responsibilities hidden by larger frameworks.

## The five parts

| Part | Tutorial code | Responsibility |
|---|---|---|
| Model | [`models.py`](../../tutorial/src/mini_agent/models.py) | Return final text or propose tool calls |
| Tool registry | [`tools.py`](../../tutorial/src/mini_agent/tools.py) | Bind public descriptions and schemas to local handlers |
| Loop | [`agent.py`](../../tutorial/src/mini_agent/agent.py) | Ask, validate, execute, return results, and stop |
| State | `messages` and `used_call_ids` | Preserve turn history and reject duplicate IDs |
| Boundaries | budgets, validation, and approval | Prevent unbounded or unauthorized execution |

OpenAI's agent overview separates model configuration, tools, state, and execution environments; when you build directly on model responses, your application owns the loop, history, and local tool execution. [Agents](https://developers.openai.com/api/docs/guides/agents)

## Read the model boundary first

`ModelClient.complete(messages, tools)` returns a small `ModelReply`: content, tool calls, and a finish reason. `ScriptedModel` implements that same interface without a network request. This keeps the Agent loop independent from a changing provider SDK and makes tests deterministic.

## A tool description is not the function

[`example_tools.py`](../../tutorial/src/mini_agent/example_tools.py) separates the Python handler, application validation, and the model-visible name, description, and JSON Schema. `required` declares mandatory properties and `additionalProperties: false` rejects undeclared properties. [JSON Schema objects](https://json-schema.org/understanding-json-schema/reference/object)

Only explicitly registered handlers can execute. Model-generated names and arguments are untrusted input; the application must never `eval` them or dynamically search for matching local functions.

## Follow the seven trace events

Run `mini-agent-demo` and compare its output with `Agent.run()`:

1. Send current messages and public tool specs to the model.
2. Receive final text or one or more proposed tool calls.
3. Validate the entire batch before executing any call.
4. Append the assistant message containing the tool calls.
5. Execute approved handlers and append results using matching call IDs.
6. Ask the model again with the expanded history.
7. Return only after a normal stop with non-empty final text.

Function calling is a multi-step application conversation, not remote execution performed by the model. [OpenAI Function calling](https://developers.openai.com/api/docs/guides/function-calling) DeepSeek likewise requires the assistant tool-call message and matching tool result before the next request. [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)

The final allowed model turn cannot start another tool execution: there would be no remaining model call to consume the result and complete the task.

## Exercises

Change one thing at a time in `demo.py`, observe the failure, then restore it:

1. Change the tool name to `unknown_tool`.
2. Add an undeclared `extra` argument.
3. Construct the Agent with `max_model_turns=1`.

Then run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Connect the real model last

[`real_deepseek.py`](../../tutorial/src/mini_agent/real_deepseek.py) translates DeepSeek Chat Completions responses into the same `ModelReply`; it does not replace the loop.

```bash
export DEEPSEEK_API_KEY="your key"
mini-agent-deepseek
```

This sends a real request and may incur charges. The adapter explicitly uses `deepseek-v4-pro`; current model identities, provider behavior, pricing links, and separately verified call examples belong in the [Model Manual](https://github.com/normalpeople553/HowToCallLLM/tree/main/models/deepseek).

Continue with [02 · Structured Output and Validation](02-structured-output-and-validation.md).
