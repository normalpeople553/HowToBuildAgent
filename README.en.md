# Agent Manual

[中文](README.md) · English

A practical manual that starts with a real online model call. Humans can follow the course, coding Agents can implement and review against repository rules, and repository-aware Agents can enter teaching mode to teach the principles interactively.

## Three entry points

| Goal | Entry | Contents |
|---|---|---|
| Learn Agent development myself | [Human Guide](human/README.en.md) | Lessons 00–08, runnable code, and completion gates |
| Ask a coding Agent to implement or review | [Agent Guide](agents/README.en.md) | Task routing, implementation constraints, sources, tests, and delivery rules |
| Ask my Agent to teach me | [Agent Teaching Mode](agents/TEACHING.en.md) | Diagnosis, incremental lessons, exercises, quizzes, feedback, and local progress |

## Hand this repository to your Agent

Send a repository-aware Agent this prompt:

> Read https://github.com/normalpeople553/HowToBuildAgent. Read `AGENTS.md` and `agents/TEACHING.en.md` completely, then enter teaching mode and begin with the pre-course diagnosis. Advance one concept at a time. Ask me to predict and practice before giving hints or feedback; do not complete exercises for me.

For implementation rather than teaching, ask it to follow `AGENTS.md` and `agents/README.en.md`, then report local tests, live API checks, and unverified boundaries separately.

## First live run

The tutorial defaults to the online `deepseek-v4-pro`; no local model installation is required:

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
export DEEPSEEK_API_KEY="your DeepSeek API key"
mini-agent-demo
```

This makes a real API request and may incur charges. The weather tool returns explicitly simulated teaching data. See the [Human Guide](human/README.en.md) for the complete course.

## Scope

- This repository covers Agent loops, tools, validation, state, memory, retrieval, MCP, testing, authorization, and deployment.
- The [Model Manual](https://github.com/normalpeople553/HowToCallLLM) maintains exact provider model IDs, parameters, pricing links, and model-calling source that has been run.
- `ScriptedModel` is a deterministic test double, not live-provider evidence or the tutorial default.
- Learning progress is stored under the Git-ignored `.learning/` directory only after the learner agrees.

Local checks do not call a model API:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Licensed under the [Unlicense](LICENSE).
