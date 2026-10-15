# Agent Manual

[中文](README.md) · English

A runnable learning path for first-time Agent developers. Start in an empty environment, run an offline model–tool loop, then learn validation, loop control, state, retrieval, MCP, testing, and authorization.

You do not need an Agent framework or an API key for the first lesson. The [`tutorial`](tutorial/) project uses a deterministic scripted model first; after you understand the control flow, the same loop can be connected to a real model.

## Start now

Use Python 3.10 or later:

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
mini-agent-demo
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. A successful run shows two model decisions with one tool execution between them. It makes no network request, and the weather result is explicitly simulated.

First-time readers should begin with [00 · Read This First](en/docs/00-read-this-first.md).

## Learning path

| Stage | Task | Chapter |
|---|---|---|
| 00 | Set up the environment and run the free offline demo | [Read This First](en/docs/00-read-this-first.md) |
| 01 | Understand the model, tool, history, and stop-condition loop | [Your First Agent](en/docs/01-from-model-call-to-first-agent.md) |
| 02 | Reject malformed and invalid arguments | [Structured Output and Validation](en/docs/02-structured-output-and-validation.md) |
| 03 | Add tools and bound routing, retries, and loops | [Multiple Tools and Loop Control](en/docs/03-multiple-tools-routing-and-loops.md) |
| 04 | Separate history, business state, summaries, and memory | [State, Memory, and Context](en/docs/04-state-memory-and-context.md) |
| 05 | Add a permission-aware knowledge base | [Retrieval and Knowledge Bases](en/docs/05-retrieval-and-knowledge-bases.md) |
| 06 | Understand what MCP does—and what it does not do | [MCP and External Tools](en/docs/06-mcp-and-external-tools.md) |
| 07 | Test trajectories and record useful diagnostic data | [Testing and Observability](en/docs/07-testing-evaluation-and-observability.md) |
| 08 | Add authorization, approval, sandboxing, and deployment boundaries | [Safety and Deployment](en/docs/08-security-confirmation-and-deployment.md) |

## Code map

| File | Role |
|---|---|
| [`models.py`](tutorial/src/mini_agent/models.py) | Stable model boundary plus the deterministic scripted model |
| [`tools.py`](tutorial/src/mini_agent/tools.py) | Tool registration, public schemas, argument validation, and execution |
| [`agent.py`](tutorial/src/mini_agent/agent.py) | The complete bounded model–tool loop |
| [`approvals.py`](tutorial/src/mini_agent/approvals.py) | Application-owned approval policies for side effects |
| [`tracing.py`](tutorial/src/mini_agent/tracing.py) | Events used by tests and diagnostics |
| [`demo.py`](tutorial/src/mini_agent/demo.py) | First complete offline trajectory |
| [`real_deepseek.py`](tutorial/src/mini_agent/real_deepseek.py) | Real-model adapter to run only after the offline lesson |

## Repository boundary

- This repository teaches Agent application design and implementation.
- The [Model Manual](https://github.com/normalpeople553/HowToCallLLM) maintains exact model IDs, provider parameters, pricing links, and model-calling source that has been run against real APIs.

Function calling is a multi-step application flow; compare [OpenAI Function calling](https://developers.openai.com/api/docs/guides/function-calling) and [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/). Object constraints follow [JSON Schema](https://json-schema.org/understanding-json-schema/reference/object). Provider features can change, so one compatible interface must not be treated as proof that all models behave identically.

## Verification

This command runs local link, translation, and Mini Agent trajectory tests without calling a model API:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

`mini-agent-demo` is also offline. Only `mini-agent-deepseek`, run after you set `DEEPSEEK_API_KEY`, sends content to a provider and may incur charges. See the [tutorial README](tutorial/README.md) for the exact boundary.

Licensed under the [Unlicense](LICENSE).
