# 09 · Thread 与 Turn：把模型循环升级为 Agent 内核

[English](../en/docs/09-thread-and-turn-kernel.md) · [目录](../README.md) · [上一章](08-权限安全人工确认与部署.md)

前八章关注“一个请求怎样安全地完成”。这一章把它扩展成可以承载多轮任务的最小内核。下面的结构是本项目的教学约定，不是某个厂商 API 的通用字段标准。

## 1. 四层结构

| 层级 | 生命周期 | 本项目类型 | 负责什么 |
|---|---|---|---|
| Thread | 多个用户任务 | `AgentThread` | 保存已完成历史、Turn 列表和当前活动状态 |
| Turn | 一次用户提交 | `Turn` | 从开始到完成、失败或中断的一次任务 |
| Item | Turn 内的一个事实 | `ThreadItem` | 用户消息、模型响应、工具请求、工具结果或最终回答 |
| Event | 状态变化通知 | `KernelEvent` | 让界面、日志和测试观察内核，而不介入控制流 |

源码入口是 [`core.py`](../tutorial/src/mini_agent/core.py)。原来的 [`Agent`](../tutorial/src/mini_agent/agent.py) 现在是兼容外观：`run()` 自动创建一个 Thread 并运行一个 Turn；需要连续对话时使用 `create_thread()` 与 `run_turn()`。

## 2. Turn 不等于一次模型请求

一个 Turn 可以包含多次模型请求：模型请求工具，程序执行并回传结果，然后再次请求模型。为了避免两个“turn”混在一起，内核把每次模型请求称为 model step，并使用 `max_model_steps` 限制次数。旧参数 `max_model_turns` 暂时保留为兼容别名；同时传入两个不同值会被拒绝。

```text
Thread
├── Turn 1
│   ├── user_message
│   ├── model_response（请求工具）
│   ├── tool_call
│   ├── tool_result
│   ├── model_response（最终正文）
│   └── assistant_message
└── Turn 2
    └── ...
```

## 3. 状态机

Thread 只有是否正在执行的最小状态：

```text
idle ── start_turn ──> active ── Turn 结束 ──> idle
```

Turn 有四个状态：

```text
in_progress ──> completed
            ├─> failed
            └─> interrupted
```

同一个 Thread 同时只能有一个活动 Turn。不存在的 Thread、活动期间重复启动、空输入和冲突预算都会在进入模型循环前被拒绝。

## 4. 为什么 Item 和 Event 要分开

Item 是任务内容的一部分，回答“发生了什么”；Event 是观察接口，回答“什么时候发生了状态变化”。例如，一个工具调用会留下 `tool_call` Item，同时发出 `item_added` 与 `tool_started` Event。这样客户端可以实时更新界面，测试也可以断言生命周期，而不必解析最终回答文本。

事件带有递增序号、`thread_id`、`turn_id` 和可选 `item_id`。这些 ID 用于关联，不把事件到达顺序误当成业务授权。

## 5. 完成历史与失败审计分离

成功 Turn 的消息会留在 Thread 的模型可见历史中，下一 Turn 会看到此前用户消息和最终回答。失败或中断时，内核保留 Turn、Item、错误与 Event 供排障，但回滚该 Turn 尚未完成的模型消息序列，避免下一次请求继承缺少工具结果的非法历史。

这不是数据库事务，也不能撤销已经发生的外部副作用。真实写工具仍需要执行点授权、幂等键和业务补偿。

## 6. 多轮使用

```python
agent = build_demo_agent(api_key)
thread = agent.create_thread()

first = agent.run_turn(thread.id, "杭州天气如何？")
second = agent.run_turn(thread.id, "刚才的结果来自哪里？")

print(first.thread_id == second.thread_id)  # True
print(first.turn_id == second.turn_id)      # False
```

`AgentResult` 现在同时提供最终回答、模型消息、旧版执行轨迹，以及 `thread_id`、`turn_id`、Items 和 Events。一次性示例继续使用 `agent.run(...)`，旧教程代码不需要改写。

## 7. 中断边界

`interrupt_turn(thread_id, turn_id)` 是协作式中断：它设置中断请求，内核会在模型返回后或下一个工具执行前停止。它不能强制杀死正在阻塞的 SDK 调用或工具函数；生产实现还需要支持超时和取消的异步客户端、进程隔离与资源回收。

## 8. 当前 v1 明确不做什么

- Thread 只保存在当前 Python 进程内，没有数据库持久化和恢复；
- 模型与工具接口仍是同步的，没有流式输出和并行工具调度；
- 没有上下文压缩、分支、队列、MCP、多 Agent 或跨进程事件总线；
- Item 内容没有自动脱敏，调用者不能把完整事件日志直接公开；
- 它是解释核心边界的教学内核，不是生产框架。

先保持这些边界，才能在后续加入持久化、异步执行或多 Agent 时，仍然知道新增能力属于 Thread、Turn、Item 还是 Event。

## 9. 验收

运行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

[`test_kernel.py`](../tests/test_kernel.py) 覆盖：完整工具 Turn、同一 Thread 的连续 Turn、失败历史回滚、只读快照、未知 Thread 和模型调用期间的协作式中断。

- [ ] 能解释 Turn 为什么可以包含多次 model step；
- [ ] 能画出 Thread 与 Turn 的状态机；
- [ ] 能区分 Item 与 Event；
- [ ] 能说明失败审计为什么保留，而模型历史为什么回滚；
- [ ] 能指出这个 v1 与生产内核之间的明确差距。
