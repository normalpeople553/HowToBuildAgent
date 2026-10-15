# 00 · Read This First

[中文](../../docs/00-开始前先看这页.md) · [Contents](../../README.en.md)

This page assumes only basic Python. The goal is to run a complete Agent before learning the terminology.

## What you will run

The first example follows a complete function-calling loop: the model proposes `get_weather`, the application validates and executes it, the result is appended as a tool message, and the model returns a final answer. Function calling is a multi-step application flow; the model does not execute your local Python function by itself. [OpenAI Function calling](https://developers.openai.com/api/docs/guides/function-calling) · [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)

## Setup

Use Python 3.10 or later:

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
mini-agent-demo
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The demo uses `ScriptedModel`, so it is deterministic, offline, and needs no API key. The weather result is explicitly simulated.

The trace should contain, in order: a model request, a response asking for one tool, tool start and finish events, another model request, a final model response, and `turn_finished`.

## Verify the local logic

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

These tests make no model API request. They cover the successful loop, unknown tools, duplicate call IDs, the final-turn boundary, local links, and translation pairs. Passing them verifies the application logic under fixed inputs, not provider availability.

## Reading order

1. [`demo.py`](../../tutorial/src/mini_agent/demo.py)
2. `Agent.run()` in [`agent.py`](../../tutorial/src/mini_agent/agent.py)
3. [`example_tools.py`](../../tutorial/src/mini_agent/example_tools.py)
4. [`tools.py`](../../tutorial/src/mini_agent/tools.py)
5. [`models.py`](../../tutorial/src/mini_agent/models.py)

Continue with [01 · From a Model Call to Your First Agent](01-from-model-call-to-first-agent.md). Connect the real model only after you can explain the loop and pass the offline tests. Running `mini-agent-deepseek` with `DEEPSEEK_API_KEY` sends a real request and may incur charges; current model details belong in the [Model Manual](https://github.com/normalpeople553/HowToCallLLM/tree/main/models/deepseek).
