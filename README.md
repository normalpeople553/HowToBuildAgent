# Agent 说明书

中文 · [English](README.en.md)

给第一次开发 Agent 的人准备的一条可运行学习路线：从 DeepSeek 在线 API 开始，先跑通一次真实的模型—工具闭环，再逐步理解参数校验、循环、状态、检索、MCP、测试和权限。

你不需要先安装本地模型，也不需要先学 Agent 框架。仓库里的 [Mini Agent](tutorial/) 默认调用 `deepseek-v4-pro`：模型真实决定是否请求工具，你的程序负责校验、执行并回传结果。

## 现在就开始

准备 Python 3.10 或更高版本，然后执行：

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
mini-agent-demo
```

Windows PowerShell 使用 `$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"` 设置 Key。成功后你会看到一次真实轨迹：DeepSeek 请求 `get_weather`，程序执行工具，再把工具结果交回 DeepSeek，最后得到正文。调用会联网并可能计费；天气工具本身返回明确标注的教学模拟数据。

第一次阅读请从 [00 · 开始前先看这页](docs/00-开始前先看这页.md) 开始。它会解释每条命令、目录和成功标准。

## 最终会做出什么

```text
用户输入
   ↓
Agent 循环 ──→ 模型：回答，或提出工具调用
   ↑                    ↓
状态与轨迹 ←── 工具结果 ←── 校验、权限、执行
```

学完后，你应当能够独立说明并实现：

- 为什么模型不能直接执行本机函数；
- 如何把工具说明与真正的处理函数分开；
- 如何校验模型生成的工具名和参数；
- 如何保存 assistant 工具请求与对应的 tool 结果；
- 如何用轮数、输出长度、权限和人工确认限制 Agent；
- 如何用固定轨迹测试循环，而不是反复付费碰运气；
- 什么时候接知识库、MCP 或多 Agent，什么时候不该接。

## 学习路线

| 顺序 | 你要完成的任务 | 阅读入口 |
|---|---|---|
| 00 | 配好环境，跑通 DeepSeek 真实工具调用 | [开始前先看这页](docs/00-开始前先看这页.md) |
| 01 | 看懂模型、工具、历史和停止条件怎样组成闭环 | [从模型调用到第一个 Agent](docs/01-从模型调用到第一个Agent.md) |
| 02 | 拒绝非法 JSON、未知字段和不合业务规则的参数 | [结构化输出与参数校验](docs/02-结构化输出与参数校验.md) |
| 03 | 增加多个工具，并控制循环、重试和预算 | [多工具、路由与循环控制](docs/03-多工具路由与循环控制.md) |
| 04 | 区分消息历史、业务状态、摘要和长期记忆 | [状态、记忆与上下文](docs/04-状态记忆与上下文管理.md) |
| 05 | 给 Agent 接入有权限边界的知识库 | [检索与知识库](docs/05-检索与知识库.md) |
| 06 | 理解 MCP 解决什么问题，不把协议当成 Agent | [MCP 与外部工具协议](docs/06-MCP与外部工具协议.md) |
| 07 | 测试完整执行轨迹，记录可排障信息 | [测试、评估与可观测性](docs/07-测试评估与可观测性.md) |
| 08 | 给写操作加授权、确认、沙箱和部署边界 | [权限、安全与部署](docs/08-权限安全人工确认与部署.md) |

## 代码地图

| 文件 | 初学时只需要知道什么 |
|---|---|
| [`real_deepseek.py`](tutorial/src/mini_agent/real_deepseek.py) | 把 DeepSeek 的真实响应转换成 Agent 循环使用的统一结构 |
| [`models.py`](tutorial/src/mini_agent/models.py) | 定义 Agent 循环依赖的模型返回结构；脚本模型只供单元测试 |
| [`tools.py`](tutorial/src/mini_agent/tools.py) | 注册工具、公开 Schema、解析与校验参数、执行函数 |
| [`agent.py`](tutorial/src/mini_agent/agent.py) | 整个 Agent 循环；先从 `run()` 开始读 |
| [`approvals.py`](tutorial/src/mini_agent/approvals.py) | 有副作用的工具由程序请求确认，不让模型自己批准 |
| [`tracing.py`](tutorial/src/mini_agent/tracing.py) | 记录模型与工具的执行步骤，供测试和排障 |
| [`demo.py`](tutorial/src/mini_agent/demo.py) | 使用 DeepSeek V4 Pro 的第一条真实工具轨迹 |

## 与模型说明书的边界

- **本仓库**讲怎样构建 Agent 应用：循环、工具、状态、记忆、检索、权限、测试和部署。
- **[模型说明书](https://github.com/normalpeople553/HowToCallLLM)** 维护准确模型 ID、厂商参数、价格入口和经过真实运行的模型调用源码。

真实模型的能力和接口会变化。本仓库只在需要连接模型时引用对应厂商说明，不把一种兼容接口推成所有模型的共同能力。工具调用的基本流程可对照 [OpenAI Function calling](https://developers.openai.com/api/docs/guides/function-calling) 与 [DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)；JSON 对象约束以 [JSON Schema](https://json-schema.org/understanding-json-schema/reference/object) 为准。

## 验证范围

下面的命令运行本地链接、翻译清单和 Mini Agent 轨迹测试，不会请求模型 API：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

`mini-agent-demo` 和 `mini-agent-multi` 都会把示例消息发送给 DeepSeek 并可能计费。单元测试使用脚本响应，不请求模型；脚本模型是测试替身，不是教程默认模型。当前验证边界和真实调用方法见 [教学项目说明](tutorial/README.md)。

本项目采用 [Unlicense](LICENSE)。
