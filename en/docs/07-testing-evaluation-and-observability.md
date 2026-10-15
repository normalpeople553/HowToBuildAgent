# 07 · Testing, evaluation and observability

[中文](../../docs/07-测试评估与可观测性.md) · [Contents](../../README.en.md)

Agent testing cannot be reduced to “the final sentence looked good.” Test deterministic code, tool traces, result quality, cost, latency and safety boundaries. NIST AI RMF places measurement and risk management across the AI lifecycle; this chapter applies that principle to Agent engineering. [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

The executable tests are in [`tests/test_tutorial_agent.py`](../../tests/test_tutorial_agent.py), and trace events are defined in [`tracing.py`](../../tutorial/src/mini_agent/tracing.py). Run `python3 -m unittest discover -s tests -p 'test_*.py'`; this does not call a model API.

## 1. Four test layers

| Layer | Model required? | Examples |
|---|---|---|
| Unit | No | Schema checks, authorization functions, idempotency and stop rules |
| Trace | Can be no | Construct assistant/tool messages and verify branches and IDs |
| Live-model evaluation | Yes | Tool selection, arguments, result correctness and stability |
| End-to-end business test | Usually | Real authorization, downstream services and audit in isolation |

Mocks establish control flow, not provider availability or actual model routing. One live pass does not establish reliability for every input. This matches the [Model Manual evidence policy](https://github.com/normalpeople553/HowToCallLLM/blob/main/en/docs/evidence-policy.md).

## 2. Evaluation sets include failures

Each case should include input, required state, allowed/forbidden tools, result constraints and risk labels. Cover normal, ambiguous, unsupported, tool-failure, unauthorized, prompt-injection, oversized, duplicate and confirmation-required cases.

Graders may be deterministic rules, human labels or models. Prefer deterministic checks for tools, arguments, authorization, citations and state. Calibrate model grading against human labels for qualities that cannot be encoded directly. [OpenAI Graders as one official implementation reference](https://platform.openai.com/docs/api-reference/graders)

## 3. Traces explain failures

Use a `trace_id` per task and a span per model or tool call. Record model/config version, turns, tool name, latency, termination, token/cost, error class and safety decision. Do not log keys, full user content, sensitive tool responses or hidden reasoning by default.

Define stable failure classes before dashboards; otherwise every incident becomes an unactionable “Agent failure.”

## 4. Release gates

Project recommendation: rerun relevant slices and a fixed regression set whenever models, prompts, tool schemas, routing, memory or retrieval change. Release only when task success, high-impact false actions, cost and P95 latency meet business-specific thresholds. There is no universal passing score.

## Checklist

- [ ] Unit, trace, live and end-to-end evidence are labeled separately.
- [ ] The set includes failures, attacks and unauthorized cases.
- [ ] Tool traces, final result, cost and latency all have metrics.
- [ ] Logs are redacted and have a retention period.
- [ ] Changes rerun the relevant regression set.
- [ ] Release thresholds match business risk.
