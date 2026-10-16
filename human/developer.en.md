# Developer Track

[Choose a Track](README.en.md) · [Complete Beginner](beginner.en.md) · [Developer Teaching Mode](../agents/TEACHING-DEVELOPER.en.md) · [中文](developer.md)

This track assumes you can independently run, read, and modify code and understand functions, mappings, exceptions, HTTP, and environment variables. It focuses on protocol boundaries, state transitions, failure paths, and engineering verification.

Run `mini-agent-demo` using the setup in [Lesson 00](../en/docs/00-read-this-first.md), then inspect the two model requests, assistant tool call, local execution, tool result, and stop condition rather than only the final text.

## Course focus

| Lesson | Engineering question | Chapter |
|---|---|---|
| 00 | How does the provider adapter enter a stable loop? | [Live call](../en/docs/00-read-this-first.md) |
| 01 | What are the loop's state transitions and stop conditions? | [First Agent](../en/docs/01-from-model-call-to-first-agent.md) |
| 02 | How do JSON, schema, business, and authorization checks differ? | [Validation](../en/docs/02-structured-output-and-validation.md) |
| 03 | How are routing, batches, retries, and budgets bounded? | [Multiple tools](../en/docs/03-multiple-tools-routing-and-loops.md) |
| 04 | How are history, state, summaries, and memory separated? | [State](../en/docs/04-state-memory-and-context.md) |
| 05 | How are retrieval permissions and evidence handled? | [Retrieval](../en/docs/05-retrieval-and-knowledge-bases.md) |
| 06 | How do MCP host/client/server roles compose with the loop? | [MCP](../en/docs/06-mcp-and-external-tools.md) |
| 07 | How are trajectories tested independently from final prose? | [Testing](../en/docs/07-testing-evaluation-and-observability.md) |
| 08 | How are side effects authorized, confirmed, deduplicated, and audited? | [Safety](../en/docs/08-security-confirmation-and-deployment.md) |
| 09 | How are durable conversations, tasks, items, and events separated? | [Thread and Turn kernel](../en/docs/09-thread-and-turn-kernel.md) |

Each lesson should produce reviewable evidence: a trajectory test, a small implementation change with preserved invariants, an architecture diagram, or a code review covering a concrete failure path. Use [Developer Teaching Mode](../agents/TEACHING-DEVELOPER.en.md) for guided code reading and exercises.
