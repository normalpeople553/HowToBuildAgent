# 01 · 从模型调用到第一个 Agent

[English](../en/docs/01-from-model-call-to-first-agent.md) · [目录](../README.md) · [上一章](00-开始前先看这页.md)

这一章不再借用一个大而全的框架。我们直接拆开刚才跑过的 Mini Agent，弄清楚一个 Agent 最少由哪些部分组成，以及每一部分为什么必须由应用程序掌控。

## 1. Agent 不是“会聊天的模型”

本教程把 Agent 定义为一种应用结构：应用反复向模型询问下一步，允许模型在预先声明的范围内请求工具；应用负责校验、授权和执行，再在满足停止条件后返回结果。

它至少有五部分：

| 部分 | 本项目对应位置 | 负责什么 |
|---|---|---|
| 模型适配器 | [`real_deepseek.py`](../tutorial/src/mini_agent/real_deepseek.py) | 调用 DeepSeek，并返回正文或工具请求 |
| 工具注册表 | [`tools.py`](../tutorial/src/mini_agent/tools.py) | 保存公开说明、参数契约和本地处理函数 |
| 循环 | [`agent.py`](../tutorial/src/mini_agent/agent.py) | 请求模型、执行工具、回传结果、判断结束 |
| 状态 | `messages` 与 `used_call_ids` | 保存本轮历史，防止调用 ID 重复 |
| 边界 | 轮数、长度、校验与批准策略 | 阻止无限循环、越权和无界输出 |

OpenAI 的 Agent 文档把模型、指令、工具、状态和执行环境作为不同配置或资源；直接使用模型响应构建 Agent 时，应用需要自己管理循环、工具执行和历史。[Agents](https://developers.openai.com/api/docs/guides/agents) 本教程选择自己写循环，是为了先看清这些责任，不是说实际项目不能使用 SDK 或框架。

## 2. 先看真实模型怎样接入

打开 [`real_deepseek.py`](../tutorial/src/mini_agent/real_deepseek.py)。`DeepSeekChatModel.complete(messages, tools)` 使用 DeepSeek 在线 API，并把厂商 SDK 回包转换为 `ModelReply`：

- `content`：最终正文，可能为空；
- `tool_calls`：模型提出的工具请求；
- `finish_reason`：这次生成为什么结束。

请求明确使用 `deepseek-v4-pro`、`https://api.deepseek.com`、`tool_choice="auto"`，并关闭思考模式。型号、服务地址、工具字段与思考开关均可在 DeepSeek 官方 [Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/) 核对。`demo.py` 从环境变量读取 Key 后创建这个真实适配器，不安装本地模型。

这是第一个重要设计：**默认用真实在线模型学习，但仍把 Agent 循环依赖的最小契约固定下来，把易变化的厂商请求放在适配器中。** 型号、参数和价格由[模型说明书](https://github.com/normalpeople553/HowToCallLLM)与厂商官方页面核对，不散落进循环代码。

## 3. 工具说明和执行函数是两件事

打开 [`example_tools.py`](../tutorial/src/mini_agent/example_tools.py)，你会看到三部分：

1. `get_weather`：真正会被 Python 执行的函数；
2. `validate_weather_arguments`：应用侧的参数与业务边界；
3. `Tool(...)`：名称、用途和 JSON Schema，供模型判断怎样提出请求。

函数工具通常用 JSON Schema 描述输入；`required` 声明必填属性，`additionalProperties: false` 拒绝未定义的额外属性。[JSON Schema object](https://json-schema.org/understanding-json-schema/reference/object) 但 Schema 只是给模型和结构校验器的契约，不能代替用户权限、资源归属或业务状态检查。

`ToolRegistry` 只会执行显式注册的处理器。即使模型返回 `delete_everything`，程序也不会用反射、`eval` 或字符串拼接寻找一个同名函数。模型输出始终是不可信输入。

## 4. 按七步轨迹读 `Agent.run()`

再次运行：

```bash
mini-agent-demo
```

然后把输出与 [`Agent.run()`](../tutorial/src/mini_agent/agent.py) 对照。

### 4.1 `model_request`

程序把当前 `messages` 和 `tools.public_specs()` 交给模型。工具公开说明告诉模型“可以请求什么”，但不包含 Python 函数对象，也不会授予系统权限。

### 4.2 `model_response`

模型可能直接返回正文，也可能返回工具调用。函数调用是多步骤对话，不是模型替应用执行函数。[OpenAI Function calling](https://developers.openai.com/api/docs/guides/function-calling)

### 4.3 整批准备

`_prepare_batch` 在任何工具执行前完成：

- 工具名必须在注册表；
- 调用 ID 非空且不能重复；
- 参数必须是 JSON 对象；
- 参数还要通过具体工具的本地校验。

先校验整批，避免两个调用中第一个已经产生影响、第二个才发现非法的半完成状态。

### 4.4 保存 assistant 工具请求

程序把包含 `tool_calls` 的 assistant 消息完整加入历史。下一次请求需要知道模型刚才提出过什么，工具结果才能通过 `tool_call_id` 与原请求配对。DeepSeek 的工具调用指南同样要求先加入模型消息，再加入对应的 tool 消息。[DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)

### 4.5 执行并保存结果

应用调用本地处理器，把结果序列化为字符串，并限制最大长度。真实项目还应对每个工具增加超时、资源限制、敏感字段清理和业务审计；本项目先保留最小接口。

### 4.6 再次请求模型

新的 `messages` 已包含用户问题、assistant 的工具请求和 tool 结果。模型据此生成最终回答，也可以继续请求另一个工具，所以循环会再次判断。

### 4.7 `turn_finished`

只有没有待处理工具、`finish_reason == "stop"` 且最终正文非空时，程序才返回 `AgentResult`。如果达到最大轮数，最后一轮的新工具不会被执行，因为执行之后已经没有预算让模型读取结果并完成回答。

## 5. 用固定测试制造三个错误

第一次成功路径使用真实 DeepSeek；异常路径不应靠反复付费碰运气。打开 [`tests/test_tutorial_agent.py`](../tests/test_tutorial_agent.py)，其中用 `ScriptedModel` 固定模型响应，稳定构造：

1. 未注册的 `unknown_tool`；
2. 多出的 `extra` 参数；
3. `max_model_turns=1` 时仍请求工具；
4. 重复的工具调用 ID；
5. 未经批准的写操作。

随后运行测试确保恢复正确：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## 6. 分清默认模型和测试替身

本教程默认入口从一开始就是 DeepSeek：

- `mini-agent-demo`：真实 DeepSeek 单工具闭环；
- `mini-agent-multi`：真实 DeepSeek 多工具任务；
- `ScriptedModel`：只在单元测试中复现指定响应，不是本地模型，也不是教程运行入口。

真实调用可能计费，并受网络、Key、余额、限流与厂商服务状态影响；固定测试不请求 API，只验证本地控制逻辑。适配器当前明确使用 `deepseek-v4-pro`；不要把 `OpenAI-compatible` 理解为所有厂商、型号和思考模式都完全一致。DeepSeek 当前型号、价格入口和经运行的调用示例见[模型说明书](https://github.com/normalpeople553/HowToCallLLM/tree/main/models/deepseek)。

## 7. 本章完成标准

- [ ] 能画出“模型请求 → 工具执行 → 工具结果 → 再次请求”的闭环；
- [ ] 能说明模型可见工具 Schema 与本地处理函数的区别；
- [ ] 知道为什么必须保留 assistant 工具请求与 `tool_call_id`；
- [ ] 知道为什么先校验整批，再执行任何工具；
- [ ] 知道最终答案、工具调用和异常停止是三种不同路径；
- [ ] 已用 DeepSeek 跑通过成功路径，也能用固定响应测试异常路径。

下一章会把“参数合法”拆成 JSON 语法、Schema 结构和业务规则三层：[02 · 结构化输出与参数校验](02-结构化输出与参数校验.md)。
