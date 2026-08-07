---
name: review-activation-performance
description: Use Growth Lab's implemented activation-review Executor to evaluate a released onboarding or first-value change against its measurement contract, primary metric, guardrails, uncertainty, and confounders. Use when deciding to continue collecting, ship, iterate, roll back, stop, or investigate measurement.
---

# Review activation performance

1. Read repository `AGENTS.md` and `DATA.md`, determine the current Product workspace, then read its `SOUL.md`.
2. Read `../../../executors/review-activation-performance/SKILL.md` and its required decision-rules reference completely.
3. Read the owning activation Model Memory, including the measurement contract, implementation, release or exposure record, and baseline.
4. Invoke `$read-product-events` for supplied exports and follow the canonical review method.
5. Write the dated aggregate review and one next action to `memory/run-product-activation-loop/`.
6. Before replying, read `../growth-lab/references/result-presentation.md`.
