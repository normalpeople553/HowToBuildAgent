# 06 · MCP and external tool protocols

[中文](../../docs/06-MCP与外部工具协议.md) · [Contents](../../README.en.md)

Model Context Protocol (MCP) standardizes connections between AI applications and services that provide context or capabilities. This chapter targets the released `2026-07-28` specification; implementations must also verify the versions supported by their client and SDK. [MCP 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [Specification](https://modelcontextprotocol.io/specification/2026-07-28)

## 1. Three roles

| Role | Responsibility |
|---|---|
| Host | User-facing AI application that manages models, consent, authorization and clients |
| Client | Protocol endpoint inside the Host communicating with one MCP Server |
| Server | Service exposing tools, resources or prompts |

Core server primitives are `tools` (executable functions), `resources` (content the application may place in context) and `prompts` (user-selectable templates). [MCP Server Overview](https://modelcontextprotocol.io/specification/2026-07-28/server)

## 2. MCP is not the Agent loop

MCP addresses discovery and invocation of external capabilities. It does not automatically provide planning, loop budgets, business authorization or human confirmation. The Host still implements Chapter 03's routing, validation, execution and stop logic.

Do not turn a stable in-process function into a remote service only to “use MCP.” It is most useful when several Hosts share a capability, standard discovery matters, or the capability needs independent authorization and lifecycle. This is a project selection recommendation.

## 3. Version and capability handling

MCP evolves. The `2026-07-28` release moved the protocol core to stateless operation and introduced optional `server/discover`, cache metadata and an Extensions framework. Do not copy `2025-11-25` session or experimental Tasks assumptions directly into the new version. [Release notes](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

Clients should call only capabilities actually discovered or negotiated. When an SDK does not support a new revision, use a revision supported by both sides rather than guessing fields.

## 4. Local and remote boundaries

| Scenario | Main risk | Project recommendation |
|---|---|---|
| Local process | Installed code runs with local-user privileges | Pin source/version; review command and file permissions |
| Remote HTTP | Token disclosure, wrong resource server, redirects and cross-server confusion | TLS, issuer/audience validation, no token passthrough |
| Third-party Server | Broad tools, untrusted content and supply-chain changes | Allowlist, least privilege, confirmation and update review |

Official MCP security guidance covers token passthrough, SSRF and authorization/session binding concerns. [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)

## Deployment checklist

- [ ] Client, Server, SDK and protocol revisions are recorded.
- [ ] Tools, resources and prompts use their distinct control boundaries.
- [ ] Remote authorization has explicit issuer, audience and scopes.
- [ ] Downstream tokens are not passed through unchanged.
- [ ] Local Server source, launch command and file privileges are reviewed.
- [ ] High-risk tools still pass Host authorization and confirmation gates.
- [ ] Timeouts, cancellation, rate limits, errors and logging are tested.
