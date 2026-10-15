# 02 · Structured output and argument validation

[中文](../../docs/02-结构化输出与参数校验.md) · [Contents](../../README.en.md)

This chapter addresses a central boundary: model output is a proposal, and application code decides whether it is safe to process. Support for JSON mode, JSON Schema and strict modes varies by provider and exact model; verify the exact-model documentation rather than treating OpenAI-compatible APIs as feature-identical. [Model Manual parameter navigation](https://github.com/normalpeople553/HowToCallLLM/blob/main/en/docs/parameters.md)

The executable counterparts are [`ToolRegistry.prepare()`](../../tutorial/src/mini_agent/tools.py) and [`validate_weather_arguments()`](../../tutorial/src/mini_agent/example_tools.py). Run `python3 -m unittest discover -s tests -p 'test_tutorial_agent.py'`; `test_extra_argument_is_rejected` proves that valid JSON with an undeclared field is rejected before the handler executes.

## 1. Three contracts

| Layer | Question | Enforcer |
|---|---|---|
| Syntax | Can the text be parsed as JSON? | JSON parser |
| Structure | Do fields, types, required keys and extra keys match the schema? | Application validator |
| Business | Does the object exist, may this user act on it, and is its state valid? | Business service |

JSON Schema uses `required` to identify properties that must be present and can use `additionalProperties: false` to reject undeclared properties. These are structural constraints, not authorization. [JSON Schema object reference](https://json-schema.org/understanding-json-schema/reference/object)

## 2. Start with a minimal schema

This is a data contract, not executable model API code:

```json
{
  "type": "object",
  "properties": {
    "order_id": {"type": "string", "minLength": 1},
    "action": {"type": "string", "enum": ["query", "cancel"]}
  },
  "required": ["order_id", "action"],
  "additionalProperties": false
}
```

Project recommendation: expose only fields required by the task, constrain lengths, ranges and enums, and avoid a free-text field that carries an executable instruction. Use the [JSON Schema keyword reference](https://json-schema.org/understanding-json-schema/keywords) for exact semantics.

## 3. Processing order

```text
Receive model output
  → check termination and nonempty output
  → parse JSON; stop on failure
  → validate the schema; stop on failure
  → perform business validation and authorization
  → request human confirmation for side effects
  → execute and record an auditable result
```

Do not retry forever. Record the failure class and permit a small retry budget only for repairable formatting errors. Authorization failures, unknown tools and business conflicts should stop.

## 4. JSON mode is not business correctness

DeepSeek's JSON Output guide requires `response_format` plus the word `json` in the prompt and warns that empty content can occur. The caller must therefore inspect the actual response instead of trusting request settings. [DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/)

Even strict schema support improves only structural adherence. Identity, authorization, existence, idempotency and business-state checks remain application responsibilities. This is the engineering boundary used by this project.

## 5. Failure policy

| Failure | Application response |
|---|---|
| Not JSON | Retain a redacted diagnostic, reject execution, optionally retry within a bound |
| Schema mismatch | Return exact field errors; never guess missing values |
| Business conflict | Return a business error; do not let the model bypass the rule |
| High-impact action | Produce a confirmation summary and wait for explicit authorization |
| Unknown or extra field | Reject and record it; do not pass it downstream |

## Checklist

- [ ] Official documentation for the exact model supports the selected mode.
- [ ] JSON parsing, schema validation and business validation are separate steps.
- [ ] Unknown fields, oversized strings and out-of-range numbers are rejected.
- [ ] Failed validation cannot reach a real tool.
- [ ] Structurally valid never means authorized.
