# Agent Manual

[Chinese](README.md) · English

Start from one model call and learn to build controllable, testable Agents that can use real tools. This repository is for people learning Agent development. Exact model IDs, parameters, pricing and real calling source remain in the **[Model Manual](https://github.com/normalpeople553/HowToCallLLM)**.

## Start here

| Your current position | Next step |
|---|---|
| You have not completed a model call | Make one call with the [Model Manual](https://github.com/normalpeople553/HowToCallLLM) first |
| You can send `messages` and read a response | Read [From one model call to your first Agent](en/docs/01-from-model-call-to-first-agent.md) |
| You already understand tool calling | Continue through the roadmap below; unfinished chapters are labeled explicitly |

## Repository boundary

- **Agent Manual:** Agent loops, tools, state, memory, retrieval, authorization, testing and deployment.
- **Model Manual:** exact-model calls, provider documentation, parameter explanations and calling source.
- **Instructions for coding agents:** remain in the Model Manual's [Agent integration instructions](https://github.com/normalpeople553/HowToCallLLM/tree/main/agents). They are not a human tutorial for building Agents.

## Roadmap

| Stage | Topic | Status |
|---|---|---|
| 01 | Model decisions, tool execution, message history and stop conditions | [Published](en/docs/01-from-model-call-to-first-agent.md) |
| 02 | Structured output and argument validation | [Published](en/docs/02-structured-output-and-validation.md) |
| 03 | Multiple tools, routing and loop control | [Published](en/docs/03-multiple-tools-routing-and-loops.md) |
| 04 | Session state, short-term memory and context management | [Published](en/docs/04-state-memory-and-context.md) |
| 05 | Retrieval and knowledge bases | [Published](en/docs/05-retrieval-and-knowledge-bases.md) |
| 06 | MCP and external tool protocols | [Published](en/docs/06-mcp-and-external-tools.md) |
| 07 | Testing, evaluation and observability | [Published](en/docs/07-testing-evaluation-and-observability.md) |
| 08 | Authorization, safety, human confirmation and deployment | [Published](en/docs/08-security-confirmation-and-deployment.md) |

All eight stages are now published. New executable code will identify its provenance, run instructions, verification scope and unverified boundaries.

## Checks

The current offline check validates local Markdown links only and makes no model API request:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Licensed under the [Unlicense](LICENSE).
