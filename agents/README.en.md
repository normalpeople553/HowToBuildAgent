# Agent Guide: Implementation, Modification, and Review

[Home](../README.en.md) · [Human Guide](../human/README.en.md) · [Teaching Mode](TEACHING.en.md) · [中文](README.md)

This page is for coding Agents that modify or review the repository. If the user wants to learn rather than delegate implementation, switch to [Teaching Mode](TEACHING.en.md).

## Route the task

| Intent | Route |
|---|---|
| Teach me, continue the course, quiz me | Route through `agents/TEACHING.en.md`, then use the beginner or developer teaching guide |
| Implement, fix, modify, or review an Agent | This guide |
| Explain one concept | The smallest relevant Human Guide chapter |
| Call a specific model | The [Model Manual](https://github.com/normalpeople553/HowToCallLLM) |

## Implementation workflow

1. Read root `AGENTS.md` and inspect the existing code, tests, language, and local changes.
2. Read only the relevant chapters and official sources.
3. Define successful, forbidden, and approval-required trajectories before editing.
4. Keep model adapters, the Agent loop, tool handlers, approval policy, and tracing separate.
5. Run local tests. Make a minimal live request only when authorized; never print keys or publish model replies.
6. Report code changes, local checks, live checks, unverified boundaries, and reproduction commands separately.

The default tutorial model is the online `deepseek-v4-pro`. Never silently replace it with a local model, scripted replies, a free tier, or another provider. `ScriptedModel` is a unit-test double only. Tool names and arguments are untrusted, call IDs must remain paired, batches are validated before execution, loops are bounded, and side effects require application-owned authorization.

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Agent configuration separates instructions, tools, guardrails, and structured outputs; this repository similarly separates teaching instructions from runtime tools and approval policy. [OpenAI Agent definitions](https://developers.openai.com/api/docs/guides/agents/define-agents)
