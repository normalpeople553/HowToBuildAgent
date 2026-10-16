# Agent 篇：实现、修改与审查规范

[项目首页](../README.md) · [人类篇](../human/README.md) · [教学模式](TEACHING.md) · [English](README.en.md)

本页给读取本仓库并执行开发任务的编程 Agent。它规定任务路由、资料边界、修改流程和验收方式；如果用户要你教他学习，而不是替他开发，请切换到[教学模式](TEACHING.md)。

## 先判断任务类型

| 用户意图 | 入口 | 你的职责 |
|---|---|---|
| “教我、带我学、继续课程、测验我” | [教学模式](TEACHING.md) | 先分成零基础或程序员路线，再按专用规则教学，不代做 |
| “帮我实现、修改、修复、审查 Agent” | 本页 | 检查项目，修改代码，按风险验证并交付 |
| “这个概念是什么” | [人类篇](../human/README.md)的最小相关章节 | 直接解释并给出处，不强制执行完整课程 |
| “怎么调用具体模型” | [模型说明书](https://github.com/normalpeople553/HowToCallLLM) | 查准确型号、参数、价格入口和经运行示例 |

## 资料地图

| 资料 | 用途 |
|---|---|
| [`human/README.md`](../human/README.md) | 人类课程路由；分别进入零基础篇和程序员篇 |
| [`docs/`](../docs/) | 中文课程正文；按任务只读相关章节 |
| [`tutorial/src/mini_agent`](../tutorial/src/mini_agent/) | 教学用 Agent 运行时与 DeepSeek 适配器 |
| [`tutorial/src/mini_agent/core.py`](../tutorial/src/mini_agent/core.py) | Thread、Turn、Item、Event 与模型—工具执行内核 |
| [`tests/test_tutorial_agent.py`](../tests/test_tutorial_agent.py) | 固定响应下的循环、校验、权限与停止边界 |
| [`tutorial/README.md`](../tutorial/README.md) | 安装、真实调用和测试边界 |
| [`agents/TEACHING.md`](TEACHING.md) | 教学分流和共同规则；再进入零基础或程序员教学文件 |

## 实现任务流程

1. 读取根目录 `AGENTS.md`，确定是教学、解释还是开发任务。
2. 检查现有代码、测试、用户项目语言与未提交修改；不覆盖无关改动。
3. 只读取与任务有关的章节、源码和官方页面，不默认把整本说明书放入模型上下文。
4. 先写清成功条件：正常轨迹、禁止轨迹、权限边界和需要保留的业务行为。
5. 修改最小范围；模型适配、Agent 循环、工具实现、批准策略和追踪保持分层。
6. 运行本地测试。需要真实验证时，使用用户授权的环境变量发起最小请求，不打印 Key，不上传模型回复或执行报告。
7. 交付时分别说明：改了什么、本地检查、真实调用、未验证边界和复现命令。

## 不可破坏的约定

- 默认教学模型是 `deepseek-v4-pro` 在线 API。不得因安装方便、费用、报错或测试便利静默替换为本地模型、脚本模型、免费型号或其他厂商。
- `ScriptedModel` 仅是测试替身。不能用它证明厂商可用、模型会选工具或线上结果正确。
- 工具名必须映射到静态注册表；模型生成的名称、JSON 和文本都是不可信输入，禁止 `eval` 或按字符串动态寻找任意本地函数。
- 一批工具在任何一个执行前先全部校验。调用 ID 必须非空、唯一并在 assistant/tool 消息中配对。
- 最后允许的模型轮次不能再执行新工具；否则没有剩余轮次让模型读取结果并完成回答。
- 有副作用的动作在执行点重新授权；模型不能批准自己的请求。默认批准策略保持拒绝。
- 上下文、工具结果、轮数和重试都必须有硬边界。日志不得默认保存 Key、完整敏感输入、隐藏思考或未脱敏工具回包。
- Thread 保存跨任务历史，Turn 表示一次任务；一次 Turn 内的多次模型请求称为 model steps，不得混用两个层级的预算和状态。

## 来源与验证

Agent 的名称、instructions、tools、guardrails 与结构化输出承担不同职责；项目据此把模型适配、教学指令、工具和批准策略分开。[OpenAI Agent definitions](https://developers.openai.com/api/docs/guides/agents/define-agents) 具体 DeepSeek 型号与协议仍以 [DeepSeek 官方文档](https://api-docs.deepseek.com/api/create-chat-completion/)和[模型说明书](https://github.com/normalpeople553/HowToCallLLM)为准。

最低检查命令：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

修改导航、课程或机器指令时同时检查本地 Markdown 链接、`translations.json` 和根目录入口。真实调用会联网并可能计费；只在授权、凭据和输入权限明确时执行。
