# Intent matching and confirmation

Use this flow when a user provides a known product together with files, data, prior results, or an implied request.

Skip redundant confirmation when the user explicitly identifies the product, task, supplied material, and requested action, and the action is read-only or already authorized. Confirm only unresolved ambiguity or a consequential boundary.

## Match read-only context

Before confirmation:

1. Match the product against Product workspaces under `workspaces/`, their `SOUL.md`, recorded product paths or URLs, and the supplied identifier.
2. Scan actual Models and their recent Memory summaries.
3. Classify supplied material as stable product evidence, timed operational evidence, a prior deliverable, configuration context, or an action request.
4. Infer the smallest task and existing Model that explain the complete input.

Do not read unrelated repositories or Memory. Do not write files during matching.

## Common intents

- Resume a Model from a previous Memory recommendation or waiting condition.
- Start a new run of an implemented Model for a different question.
- Update stable product understanding in the current Product workspace's `SOUL.md`.
- Analyze newly provided evidence in the relevant Model Memory.
- Configure a capability required by the selected Model.
- Create, modify, publish, deploy, or review an output.

## Confirm the interpretation

Respond briefly:

```text
我识别到当前产品是「<product>」，并找到了 <relevant-model-or-memory>。

我理解你希望：<one-sentence-intent>。

本轮将：
- 使用：<materials>；
- 继续：<model-and-relevant-memory>；
- 产出：<expected-output>；
- 不会：<excluded-actions>。

是否按这个理解继续？
```

When two interpretations remain plausible, show at most two alternatives.

When confirmation is required, do not update SOUL or Memory, import private data, configure credentials, create deliverables, or perform side effects before it. If the user corrects the interpretation, discard the rejected routing and rematch. Record only the confirmed intent in the resulting Memory.
