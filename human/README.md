# 人类篇：从零搭建第一个 Agent

[项目首页](../README.md) · [Agent 篇](../agents/README.md) · [让 Agent 教我](../agents/TEACHING.md) · [English](README.en.md)

人类篇给第一次开发 Agent 的人阅读。默认从 DeepSeek 在线 API 开始，不安装本地模型：先完成一次真实模型—工具闭环，再逐步理解校验、循环、状态、检索、MCP、测试和权限。

## 两种学习方式

### 自己读

按下面的顺序阅读、运行命令并完成每章检查表。遇到错误时保留脱敏后的错误体、运行命令和 Python 版本，不提供完整 Key。

### 让你的 Agent 教你

把仓库地址和下面这段话交给能够读取仓库的 Agent：

> 请先完整读取仓库根目录 `AGENTS.md` 和 `agents/TEACHING.md`，然后进入教学模式教我学习 Agent 原理。把我当作第一次开发 Agent 的学生，从课前诊断开始，一次只推进一个知识点。先让我预测和动手，再给提示与反馈；不要直接替我完成练习。默认使用仓库规定的 DeepSeek 在线模型，并在每节结束时按验收标准判断我是否真正理解。

如果你中途回来，可以说“继续教学”；Agent 应先读取本地 `.learning/progress.md`。没有进度文件时从诊断开始，不根据聊天印象伪造已完成章节。详细规则见[教学模式](../agents/TEACHING.md)。

## 学习路线

| 课次 | 你要真正做到什么 | 章节 |
|---|---|---|
| 00 | 配置 Key，完成真实 DeepSeek 工具调用，区分模型请求与本地工具 | [用 DeepSeek 跑通第一个 Agent](../docs/00-开始前先看这页.md) |
| 01 | 画出模型、工具、历史、循环与停止条件 | [从模型调用到第一个 Agent](../docs/01-从模型调用到第一个Agent.md) |
| 02 | 在执行前拒绝非法 JSON、未知字段和业务非法参数 | [结构化输出与参数校验](../docs/02-结构化输出与参数校验.md) |
| 03 | 增加工具并控制路由、调用顺序、重试和预算 | [多工具、路由与循环控制](../docs/03-多工具路由与循环控制.md) |
| 04 | 区分对话历史、业务状态、短期摘要与长期记忆 | [状态、记忆与上下文](../docs/04-状态记忆与上下文管理.md) |
| 05 | 在权限过滤之后检索，并让回答能回到证据 | [检索与知识库](../docs/05-检索与知识库.md) |
| 06 | 解释 MCP 的客户端、服务器与 Agent 循环边界 | [MCP 与外部工具协议](../docs/06-MCP与外部工具协议.md) |
| 07 | 用固定轨迹测试本地逻辑，用真实请求验证厂商链路 | [测试、评估与可观测性](../docs/07-测试评估与可观测性.md) |
| 08 | 给写操作加权限、确认、审计与部署边界 | [权限、安全与部署](../docs/08-权限安全人工确认与部署.md) |

## 第一次运行

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
mini-agent-demo
```

这会请求真实 DeepSeek API 并可能计费。Windows、错误排查、预期轨迹和安全说明都在[第 00 课](../docs/00-开始前先看这页.md)。

## 怎样检查 Agent 写得对不对

不要只看最终回答。至少检查：

- 使用准确型号、服务地址和对应官方协议；
- 模型只提出工具请求，真正执行由静态白名单映射；
- 参数在执行前完成 JSON、结构、业务和权限校验；
- assistant 工具请求与 tool 结果通过同一调用 ID 配对；
- 循环有轮数、输出和失败边界；
- 写操作不能由模型替用户批准；
- 测试替身没有被写成真实 API 成功。

可执行实现位于 [`tutorial/src/mini_agent`](../tutorial/src/mini_agent/)，本地回归位于 [`tests/test_tutorial_agent.py`](../tests/test_tutorial_agent.py)。给编程 Agent 修改项目时，使用 [Agent 篇](../agents/README.md)。
