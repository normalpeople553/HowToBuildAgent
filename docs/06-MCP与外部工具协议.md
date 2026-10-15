# 06 · MCP 与外部工具协议

[English](../en/docs/06-mcp-and-external-tools.md) · [目录](../README.md)

Model Context Protocol（MCP）用标准化协议连接 AI 应用与提供上下文或能力的服务。本章以当前已发布的 `2026-07-28` 规范为主，实现时必须同时核对客户端与 SDK 支持的协议版本。[MCP 2026-07-28 发布说明](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [规范](https://modelcontextprotocol.io/specification/2026-07-28)

## 1. 先分清三个角色

| 角色 | 职责 |
|---|---|
| Host | 面向用户的 AI 应用，管理模型、授权、同意和多个客户端 |
| Client | 在 Host 内与某个 MCP Server 通信的协议端 |
| Server | 暴露工具、资源或提示等能力的服务 |

MCP 服务器的三种核心服务端原语是：`tools`（可执行函数）、`resources`（由应用控制如何加入上下文的内容）和 `prompts`（用户可选的模板）。[MCP Server Overview](https://modelcontextprotocol.io/specification/2026-07-28/server)

## 2. MCP 不是 Agent 循环

MCP 规范解决发现和调用外部能力的协议问题；它不会自动提供任务规划、循环预算、业务授权或人工确认。Host 仍要实现第 03 章的路由、校验、执行和停止逻辑。

不要为了“用上 MCP”就把应用内一个稳定函数拆成远程服务。当能力需要被多个 Host 共用、需要标准化发现，或需要独立权限与生命周期时，MCP 才更有价值。这是项目选型建议。

## 3. 版本和能力协商

MCP 在持续演进；`2026-07-28` 将协议核心改为无状态，引入 `server/discover` 可选发现、可缓存的 list/read 结果与 Extensions 框架。不应把 `2025-11-25` 的会话和实验性 Tasks 假设直接搬到新版本。[发布说明](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

客户端应检查服务器声明的能力，只调用已协商或已发现的方法。当 SDK 尚未支持新规范时，应选择双方共同支持的版本，不靠猜测字段做兼容。

## 4. 本地与远程边界

| 场景 | 主要风险 | 项目建议 |
|---|---|---|
| 本地进程 | 安装包可执行当前用户权限下的代码 | 锁定来源和版本，审查命令与文件权限 |
| 远程 HTTP | token 泄漏、错误资源服务器、重定向和跨服务器混淆 | 使用 TLS、验证 issuer/audience，不做 token passthrough |
| 第三方 Server | 工具集过大、内容不可信、供应链变更 | 允许列表、最小权限、人工确认和更新复核 |

MCP 官方安全实践要求避免 token passthrough，并针对 SSRF、会话或授权绑定等问题提供专门建议。[MCP Security Best Practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices)

## 5. 上线前清单

- [ ] 记录客户端、服务器、SDK 和协议版本；
- [ ] 工具、资源和提示按不同控制边界处理；
- [ ] 远程调用有明确的授权服务器、audience 与 scope；
- [ ] 不将下游 token 原样透传给 MCP Server；
- [ ] 本地 Server 的安装来源、启动命令和文件权限已审查；
- [ ] 每个高风险工具仍经过 Host 权限和确认门禁；
- [ ] 超时、取消、限流、错误和日志边界已测试。
