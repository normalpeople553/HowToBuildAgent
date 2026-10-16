# 程序员篇：从模型调用到可控 Agent

[选择路线](README.md) · [零基础篇](beginner.md) · [程序员教学模式](../agents/TEACHING-DEVELOPER.md) · [English](developer.en.md)

这条路线面向能独立运行、阅读和修改代码的开发者。默认你理解函数、映射、异常、HTTP 和环境变量；课程不重复讲 Python 基础，而是聚焦 Agent 的协议边界、状态机、失败路径和工程验证。

## 快速开始

```bash
git clone https://github.com/normalpeople553/HowToBuildAgent.git
cd HowToBuildAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
mini-agent-demo
```

这会调用在线 `deepseek-v4-pro` 并可能计费。运行后不要只看最终文本；定位两次模型请求、assistant 工具调用、本地执行、tool 结果和停止条件。天气工具返回教学模拟数据。

## 建议阅读顺序

| 课次 | 工程问题 | 章节 | 源码检查点 |
|---|---|---|---|
| 00 | 厂商适配层怎样进入统一循环 | [真实调用](../docs/00-开始前先看这页.md) | [`real_deepseek.py`](../tutorial/src/mini_agent/real_deepseek.py) |
| 01 | Agent 循环的状态转移和停止条件是什么 | [第一个 Agent](../docs/01-从模型调用到第一个Agent.md) | [`core.py`](../tutorial/src/mini_agent/core.py) |
| 02 | JSON、Schema、业务与权限校验如何分层 | [结构化输出](../docs/02-结构化输出与参数校验.md) | [`tools.py`](../tutorial/src/mini_agent/tools.py) |
| 03 | 多工具、批量调用、重试和预算如何受控 | [路由与循环](../docs/03-多工具路由与循环控制.md) | `AgentKernel.start_turn()` 与工具注册表 |
| 04 | 历史、状态、摘要和长期记忆怎样分离 | [状态与上下文](../docs/04-状态记忆与上下文管理.md) | 消息构造与状态所有权 |
| 05 | 检索的权限过滤、证据和失败策略是什么 | [检索](../docs/05-检索与知识库.md) | 检索边界与引用 |
| 06 | MCP host/client/server 与 Agent 循环怎样组合 | [MCP](../docs/06-MCP与外部工具协议.md) | 协议层与决策层边界 |
| 07 | 怎样测试轨迹而不是只断言最终字符串 | [测试与可观测性](../docs/07-测试评估与可观测性.md) | [`test_tutorial_agent.py`](../tests/test_tutorial_agent.py) |
| 08 | 写操作如何授权、确认、幂等和审计 | [安全与部署](../docs/08-权限安全人工确认与部署.md) | [`approvals.py`](../tutorial/src/mini_agent/approvals.py) |
| 09 | 长期会话、单次任务、产物和事件如何分层 | [Thread 与 Turn 内核](../docs/09-Thread与Turn内核.md) | [`core.py`](../tutorial/src/mini_agent/core.py) |

## 每章的程序员验收方式

每章至少完成一种可检查产物：

- 为正常、拒绝和边界轨迹各写一个测试；
- 修改一个工具或策略，并解释没有破坏哪些不变量；
- 画出状态转移、消息协议或权限边界；
- 对一段 Agent 实现做代码审查，给出具体文件与失败路径；
- 分别说明本地测试、真实模型请求和端到端测试能够证明什么。

重点检查：工具名必须来自静态注册表；整批调用在执行前完成校验；调用 ID 非空、唯一且配对；最后一个模型轮次不再执行新工具；副作用在执行点由应用重新授权。

如果希望由 Agent 进行代码导读、提问和审查练习，使用[程序员教学模式](../agents/TEACHING-DEVELOPER.md)。
