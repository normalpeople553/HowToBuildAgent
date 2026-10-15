# 08 · Authorization, security, human confirmation and deployment

[中文](../../docs/08-权限安全人工确认与部署.md) · [Contents](../../README.en.md)

Agent security is not making the model “more obedient”; it is limiting the maximum impact of one wrong decision. OWASP identifies excessive functionality, permissions and autonomy as roots of Excessive Agency. NIST's Generative AI Profile addresses governance, measurement and risk management across the lifecycle. [OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) · [NIST Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

The tutorial keeps approval policy in [`approvals.py`](../../tutorial/src/mini_agent/approvals.py). A tool marked `requires_approval=True` is denied by `DenyAll` unless the application supplies an explicit alternative; model text cannot approve its own action.

## 1. Three minimizations

| Principle | Implementation |
|---|---|
| Least functionality | Expose only required tools; separate read from write/delete |
| Least privilege | Use current-user identity and minimum scopes, not one shared privileged credential |
| Least autonomy | Preview high-impact actions and require confirmation before execution |

Authorization must be rechecked in the tool or downstream system. A system prompt is not an authorization decision.

## 2. Treat external content as data

User text, webpages, email, documents, image text, retrieved passages and tool results may contain prompt injection. Delimit them as data and do not promote embedded instructions to system rules. Still enforce argument/schema, authorization and business checks in application code. Impact depends on business context and available agency. [OWASP Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

## 3. Confirmation binds a specific action

A useful confirmation view shows the action, target, key parameters, expected impact, reversibility, credential identity and expiry. “Continue?” is not enough for risk judgment.

Bind confirmation to an immutable action digest or request ID. If target, amount or another critical field changes after confirmation, invalidate it and ask again.

## 4. Secrets, logs and supply chain

- Inject secrets from a secret manager or process environment; never place them in code, prompts, schemas or logs.
- Apply field-level redaction, access control and retention to logs. Debug mode must not default to exporting full context.
- Pin SDK, MCP Server and tool dependency source/version; review permissions, launch commands and capability changes before updates.

OWASP's LLM/GenAI Top 10 separates supply-chain, sensitive-disclosure, improper-output-handling and unbounded-consumption risks. [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/)

## 5. Deployment boundaries

Place API services, Agent workers and high-risk tools behind independently authorized and rate-limited boundaries. Workers use task-scoped identities with network, CPU/memory, duration and concurrency limits. Side effects use business idempotency keys, and queues classify retryable versus non-retryable failures.

Prepare emergency stops by tool, user, tenant and release version so write actions can be disabled without waiting for a complete redeploy.

## Release checklist

- [ ] Tool functionality, credential privilege and Agent autonomy are minimized.
- [ ] External content is handled as untrusted data.
- [ ] High-risk confirmation binds exact parameters and expires.
- [ ] Secrets, logs and traces have redaction and access controls.
- [ ] Dependencies and MCP Servers have pinned sources and versions.
- [ ] Timeouts, rate limits, quotas, idempotency and emergency stops are tested.
- [ ] Failure traces and high-risk blocks are reviewed after launch.
