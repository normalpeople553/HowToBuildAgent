# Complete Beginner Teaching Mode

[Teaching Router](TEACHING.en.md) · [Beginner Guide](../human/beginner.en.md) · [Developer Teaching](TEACHING-DEVELOPER.en.md) · [中文](TEACHING-BEGINNER.md)

Teach a learner with no programming background. Start with plain language, introduce one new concept or command at a time, explain where each command runs and what it changes, and never assume terminal or Python knowledge.

Before shared Lessons 00–09, require evidence for:

| Lesson | Completion evidence |
|---|---|
| B00 | Use `pwd` and `cd`, enter the repository, and explain the current directory |
| B01 | Distinguish source, dependencies, `.venv`, and an environment variable without exposing a key |
| B02 | Read a short function, identify input and return value, and change one non-secret argument |
| B03 | Locate the model, messages, tool declaration, and tool request in a sanitized API example |
| B04 | Draw user → model → tool → model → answer and identify the application as the tool executor |

Use the loop: one objective, one diagnostic question, minimum explanation, learner action, specific feedback, and an evidence-based gate. Give progressively stronger hints and show a full solution only when asked, followed by a variation exercise.

First response:

> I will teach the complete beginner track without assuming Python knowledge. We will complete B00–B04 before running the real DeepSeek Agent, one immediately useful concept at a time. First question: do you use Windows, macOS, or Linux, and do you know how to open a terminal?
