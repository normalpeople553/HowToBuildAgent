# 教学项目：Mini Agent

这是《Agent 说明书》从零到一课程使用的代码。默认入口直接调用 DeepSeek V4 Pro，不安装本地模型，也不把脚本响应当成教程默认模型。

## 第一次真实调用

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
mini-agent-demo
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e tutorial
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
mini-agent-demo
```

`mini-agent-demo` 会向 DeepSeek 发送真实请求并可能计费。型号、价格和厂商调用细节以[模型说明书 DeepSeek 页面](https://github.com/normalpeople553/HowToCallLLM/tree/main/models/deepseek)与 [DeepSeek 官方 Chat API](https://api-docs.deepseek.com/api/create-chat-completion/)为准。

## 后续示例

学到多工具一章后运行：

```bash
mini-agent-multi
```

它同样使用真实 DeepSeek，并要求模型完成 `get_weather` 与 `multiply` 两个工具。天气结果仍是教学模拟数据。

## 测试边界

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

测试使用 `ScriptedModel` 固定模型返回，只用来稳定覆盖异常路径，不请求厂商 API。教学默认入口始终是 DeepSeek 在线模型。

代码包含工具白名单、参数校验、重复 ID 检查、整批预校验、模型步骤上限、工具输出长度上限、人工确认接口和轨迹记录。`core.py` 进一步提供 Thread、Turn、Item 与 Event：一次性 `Agent.run()` 仍可使用，连续任务则使用 `create_thread()` 和 `run_turn()`。完整说明见 [Thread 与 Turn 内核](../docs/09-Thread与Turn内核.md)。

它是内存内、同步的教学实现，不是可以直接承载生产业务的通用框架。
