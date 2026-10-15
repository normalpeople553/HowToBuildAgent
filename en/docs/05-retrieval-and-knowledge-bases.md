# 05 · Retrieval and knowledge bases

[中文](../../docs/05-检索与知识库.md) · [Contents](../../README.en.md)

The original RAG paper combined a parametric model with retrievable non-parametric external memory for generation. In application terms: retrieve material relevant to the question, then generate from selected evidence and an explicit task. [Original RAG paper](https://arxiv.org/abs/2005.11401)

## 1. RAG is more than uploading a file

| Stage | Input | Output | What to test separately |
|---|---|---|---|
| Ingestion | Source document | Normalized text with version and access control | Missing pages, ordering and OCR errors |
| Chunking | Normalized text | Retrievable passages | Broken semantics and tables |
| Indexing | Passages and metadata | Search index | Version, tenant and tag filters |
| Retrieval | User question | Candidate passages | Whether correct evidence enters top-k |
| Reranking | Candidates | Final evidence | Relevance and authorization |
| Generation | Question and evidence | Answer and citations | Whether evidence supports the answer |

Project recommendation: retain `document_id`, `version`, `location`, `tenant`, `acl` and traceable source text for every chunk. These fields support authorization filters, citation location and expiry.

## 2. Filter authorization before the model

Do not ask the model to decide knowledge-base access. Apply user, tenant and resource filters during retrieval; unauthorized chunks must not enter prompts or logs. OWASP lists vector and embedding weaknesses among LLM application risks, including isolation, poisoning and retrieval disclosure concerns. [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/)

## 3. Separate evidence from instructions

Retrieved text is untrusted and may contain instructions disguised as content. Delimit evidence and tell the model not to execute its instructions, but do not rely on that prompt as the sole defense. Enforce tool permissions, output validation and human confirmation in application code. [OWASP Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

## 4. Citations are a product feature

Map claims to returned document IDs and locations, then render clickable sources in application code. Do not let the model invent URLs. When evidence is insufficient or conflicting, support an explicit insufficient-evidence result and show the conflicting sources.

## 5. Evaluate retrieval and generation separately

Build questions with expected document IDs. Measure retrieval hit rate, correct abstention, authorization leakage, citation correctness and final task success separately. If the right document never enters the candidates, prompt editing alone is not the fix.

## Checklist

- [ ] Source, chunk, version and location are traceable.
- [ ] Authorization is enforced during retrieval, not by the model.
- [ ] Retrieved content is handled as untrusted input.
- [ ] Application code maps citations to real documents.
- [ ] Retrieval and answer quality are evaluated separately.
- [ ] Deletion, expiry and index rebuild paths exist.
