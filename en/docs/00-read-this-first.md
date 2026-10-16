# 00 · Run Your First Agent with DeepSeek

[中文](../../docs/00-开始前先看这页.md) · [Contents](../../README.en.md)

The first lesson does not install a local model or use a fake model as the main demo. You will call the online DeepSeek API, let the real model request a tool, execute that tool in Python, and return the result to the model.

## Configure the API key

Create a key at [DeepSeek API Keys](https://platform.deepseek.com/api_keys). Never place it in source code or commit it to Git.

```bash
export DEEPSEEK_API_KEY="your DeepSeek API key"
```

PowerShell uses `$env:DEEPSEEK_API_KEY="your DeepSeek API key"`.

## Install and run

Use Python 3.10 or later:

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
mini-agent-demo
```

This makes real API requests and may incur charges. The default is `deepseek-v4-pro`, which is listed by the current DeepSeek Chat API and supports tool calls. [Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/) Check the live [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/) page for prices.

The expected trajectory is: DeepSeek requests `get_weather`, the application validates and executes it, the result is returned as a tool message, and DeepSeek produces the final answer. The model call and tool selection are real; the weather function deliberately returns simulated teaching data.

Function calling is a multi-step application flow, and generated arguments still require application validation. [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)

## Read the code

1. [`demo.py`](../../tutorial/src/mini_agent/demo.py)
2. [`real_deepseek.py`](../../tutorial/src/mini_agent/real_deepseek.py)
3. `AgentKernel.start_turn()` in [`core.py`](../../tutorial/src/mini_agent/core.py), reached through the simple `Agent.run()` facade
4. [`example_tools.py`](../../tutorial/src/mini_agent/example_tools.py)
5. [`tools.py`](../../tutorial/src/mini_agent/tools.py)

After the live call succeeds, run the regression tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Tests use fixed scripted replies to reproduce error paths without spending API tokens. That is a test double, not the tutorial's default model. Continue with [01 · From a Model Call to Your First Agent](01-from-model-call-to-first-agent.md).
