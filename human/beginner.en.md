# Complete Beginner Track

[Choose a Track](README.en.md) · [Developer Track](developer.en.md) · [Beginner Teaching Mode](../agents/TEACHING-BEGINNER.en.md) · [中文](beginner.md)

This track assumes no programming experience. It teaches only the prerequisites required to run and understand the first Agent before joining the shared Lessons 00–08.

## Prerequisites

| Lesson | Topic | Completion evidence |
|---|---|---|
| B00 | Terminal, commands, and current directory | Use `pwd` and `cd`, and identify where a command runs |
| B01 | Files, dependencies, environment variables, and virtual environments | Explain the roles of source files, `.venv`, dependencies, and `DEEPSEEK_API_KEY` |
| B02 | Python variables, lists, dictionaries, functions, and exceptions | Read a short tutorial function and safely modify a non-secret argument |
| B03 | JSON, HTTP, APIs, requests, and responses | Locate the model, messages, tool declaration, and tool request |
| B04 | Model calls versus Agent loops | Draw user → model → tool → model → answer and identify the component that executes tools |

Do not learn unused syntax in advance. Each concept should be introduced when it appears in the repository's real code.

Use `pwd`, `ls`, and `cd` for B00. For B01, distinguish source code, installed dependencies, the project-local `.venv`, and the secret `DEEPSEEK_API_KEY`; check only whether a key exists and never print it. For B02, identify a short function's arguments, dictionary values, return value, and exception path. For B03, identify `model`, `messages`, and `tools` in a sanitized JSON request. For B04, draw the loop and explain that the application—not the model—validates and executes a local tool.

## First run

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
export DEEPSEEK_API_KEY="your DeepSeek API key"
mini-agent-demo
```

This calls the online `deepseek-v4-pro` and may incur charges. Never paste the key into chat, source, or Git. After B00–B04, continue with [Lesson 00](../en/docs/00-read-this-first.md) and use the [Beginner Teaching Mode](../agents/TEACHING-BEGINNER.en.md) for guided study.
