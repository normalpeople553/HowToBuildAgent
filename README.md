# Agent 说明书

中文 · [English](README.en.md)

一套从真实在线模型调用开始的 Agent 学习与开发手册。人可以按课程从零学习，编程 Agent 可以按仓库规范实现和审查代码，也可以切换成老师，带着你逐步理解 Agent 原理。

## 三个入口

| 你现在要做什么 | 入口 | 里面有什么 |
|---|---|---|
| 我想自己学习 Agent | [人类篇](human/README.md)：[零基础](human/beginner.md) / [程序员](human/developer.md) | 按编程基础分流，再进入对应课程、代码和验收标准 |
| 我要让编程 Agent 开发或审查 Agent | [Agent 篇](agents/README.md) | 任务路由、实现约束、来源规则、测试与交付要求 |
| 我要让我的 Agent 教我 | [教学模式](agents/TEACHING.md)：[零基础](agents/TEACHING-BEGINNER.md) / [程序员](agents/TEACHING-DEVELOPER.md) | 先判断学习路线，再采用不同讲解、练习和验收方式 |

## 直接交给你的 Agent

把仓库地址和下面这段话一起发给能够读取 GitHub 仓库的 Agent：

> 阅读 https://github.com/normalpeople553/HowToBuildAgent 。先完整读取根目录 `AGENTS.md` 和 `agents/TEACHING.md`，判断我适合零基础路线还是程序员路线，并说明依据。得到我确认后读取对应教学文件，从课前诊断开始教我学习 Agent 原理。一次只推进一个知识点，先让我预测和动手，再给提示与反馈；不要直接替我完成练习。

如果你希望它替你开发，而不是教学，把最后一句改为：

> 按 `AGENTS.md` 和 `agents/README.md` 的规范实现我的需求，并分别报告本地测试、真实 API 验证和未验证边界。

## 第一次真实运行

仓库默认使用 DeepSeek 在线 API 的 `deepseek-v4-pro`，不要求安装本地模型：

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
mini-agent-demo
```

这会发起真实 API 请求并可能计费。天气工具返回的是明确标注的教学模拟数据；完整的 Windows 命令、预期轨迹和排障方法见[人类篇](human/README.md)。

## 仓库边界

- 本仓库讲 Agent 的循环、工具、校验、状态、记忆、检索、MCP、测试、权限和部署。
- [模型说明书](https://github.com/normalpeople553/HowToCallLLM)维护具体厂商的准确模型 ID、参数、价格入口和经过运行的调用源码。
- `ScriptedModel` 只用于确定性测试，不能替代真实厂商调用，也不是教程默认模型。
- 学习进度只在用户同意后保存到 Git 忽略的 `.learning/`，不进入仓库。

本地检查不会请求模型 API：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

本项目采用 [Unlicense](LICENSE)。
