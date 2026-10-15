# Human Guide: Build Your First Agent from Zero

[Home](../README.en.md) · [Agent Guide](../agents/README.en.md) · [Let an Agent Teach Me](../agents/TEACHING.en.md) · [中文](README.md)

This guide is for first-time Agent developers. It starts with the online DeepSeek API rather than a local model: complete a real model–tool loop, then learn validation, loop control, state, retrieval, MCP, testing, and authorization.

## Learn on your own

Follow the course in order, run each command, and complete each chapter's checks. Start with [Lesson 00](../en/docs/00-read-this-first.md).

## Let your Agent teach you

Give a repository-aware Agent this prompt:

> Read `AGENTS.md` and `agents/TEACHING.en.md` completely, then enter teaching mode. Treat me as a first-time Agent developer. Begin with a short diagnosis and advance one concept at a time. Make me predict and practice before giving hints or feedback; do not complete exercises for me. Use the repository's online DeepSeek default and assess each lesson against its completion gate.

The Agent may keep progress in the Git-ignored `.learning/progress.md` after your approval. See [Teaching Mode](../agents/TEACHING.en.md).

## Course

| Lesson | Outcome | Chapter |
|---|---|---|
| 00 | Complete a real DeepSeek tool call | [First Agent with DeepSeek](../en/docs/00-read-this-first.md) |
| 01 | Explain the model–tool loop and stop conditions | [Your First Agent](../en/docs/01-from-model-call-to-first-agent.md) |
| 02 | Reject malformed and invalid arguments | [Structured Output](../en/docs/02-structured-output-and-validation.md) |
| 03 | Add tools and bound routing and loops | [Multiple Tools](../en/docs/03-multiple-tools-routing-and-loops.md) |
| 04 | Separate history, state, summaries, and memory | [State and Memory](../en/docs/04-state-memory-and-context.md) |
| 05 | Add permission-aware retrieval | [Retrieval](../en/docs/05-retrieval-and-knowledge-bases.md) |
| 06 | Explain the MCP and Agent-loop boundary | [MCP](../en/docs/06-mcp-and-external-tools.md) |
| 07 | Test trajectories and live provider paths separately | [Testing](../en/docs/07-testing-evaluation-and-observability.md) |
| 08 | Add authorization, approval, and deployment boundaries | [Safety](../en/docs/08-security-confirmation-and-deployment.md) |

Use the [Agent Guide](../agents/README.en.md) when asking a coding Agent to modify or review the implementation.
