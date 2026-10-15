# 教学项目：Mini Agent

这是《Agent 说明书》从零到一课程使用的代码。默认演示使用脚本模型，不联网、不需要 API Key；真实 DeepSeek 入口单独放在 `real_deepseek.py`。

从仓库根目录运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e tutorial
mini-agent-demo
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e tutorial
mini-agent-demo
```

第一章跑 `mini-agent-demo`；学到多工具一章后跑 `mini-agent-multi`，观察同一批两个调用怎样先全部校验、再按顺序执行。

运行真实模型前，先设置 `DEEPSEEK_API_KEY`，再执行 `mini-agent-deepseek`。它会发起真实请求并可能计费。型号、价格和厂商调用细节以[模型说明书的 DeepSeek 页面](https://github.com/normalpeople553/HowToCallLLM/tree/main/models/deepseek)为准。

教学代码有意保持很小，但仍包含工具白名单、参数校验、重复 ID 检查、整批预校验、执行轮数上限、工具输出长度上限、人工确认接口和轨迹记录。它不是可以直接承载生产业务的通用框架。
