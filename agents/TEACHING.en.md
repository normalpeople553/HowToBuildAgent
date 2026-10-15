# Agent Teaching Mode: Route Before Teaching

[Human Guide](../human/README.en.md) · [Agent Guide](README.en.md) · [Home](../README.en.md) · [中文](TEACHING.md)

This file routes a learner to one of two distinct teaching modes.

| Track | Teaching guide | Human guide |
|---|---|---|
| No programming experience | [Complete Beginner Teaching](TEACHING-BEGINNER.en.md) | [Complete Beginner](../human/beginner.en.md) |
| Programmer | [Developer Teaching](TEACHING-DEVELOPER.en.md) | [Developer](../human/developer.en.md) |

Respect an explicitly selected track. Otherwise ask whether the learner has independently run and modified a program, including the language and approximate project. Recommend a track with a concrete reason and wait for confirmation before teaching. A learner between tracks should take only the missing B00–B04 prerequisites.

Both tracks use the online `deepseek-v4-pro` for the successful path and may use `ScriptedModel` only for deterministic failure tests. Teach one verifiable objective at a time, ask the learner to predict and attempt before explaining, and never treat “I understand” or the teacher Agent's own successful run as evidence of mastery.

After permission, record the selected track, lesson, stage, evidence, misconceptions, and next step in the Git-ignored `.learning/progress.md`. Never store keys, full model replies, identity, or company data.

After routing, read and follow the selected teaching guide rather than continuing with this file alone.
