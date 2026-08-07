# Social content loop automation

Use this reference only when scheduling or repeating the social content Model. Follow root `AUTOMATION.md`.

## Readiness

Do not schedule until the same scope has run manually and its input sources, content output location, review checklist, publication boundary, metric path, Memory output, waiting conditions, and permissions are verified.

Start with `Observe` or `Recommend`. Content generation, asset generation, platform publishing, paid boosting, deletion, direct messaging, comment replies, and credential changes remain disabled until separately tested and authorized.

## Observation-only task template

```text
Run $run-social-content-loop in observation-only mode for the current Product.

Read AGENTS.md, DATA.md, AUTOMATION.md, determine the Product workspace, then read its SOUL.md, the canonical social content Model, and relevant memory/run-social-content-loop files.

For this run:
- observe only the latest completed and comparable platform/content/product data window;
- use only already authorized read-only sources and user-provided exports;
- process platform exports through $read-social-platform-export and product events through $read-product-events;
- write a dated aggregate review to the current Product workspace's memory/run-social-content-loop/;
- distinguish no material change, incomplete data, missing authorization, platform access failure, and real behavior change;
- if nothing decision-relevant changed, record that briefly and take no action;
- do not create new content, generate images, upload files, publish, delete, reply, boost, spend money, change credentials, or modify product code;
- use change policy suggest-only.
```

## Stop conditions

Stop and request user action when:

- the Product workspace or platform account is ambiguous;
- a next step requires account login, upload, API authorization, spending, publication, deletion, comment reply, or product-code modification;
- product facts cannot support the intended claim;
- source access is blocked or would violate platform terms;
- screenshot or asset rights are unclear;
- platform exports are incomplete or incomparable;
- attribution cannot separate platform exposure from product outcomes;
- repeated runs produce no usable evidence and the cadence should change.

## Idempotency

Every automated run must identify a unique campaign, platform, candidate, publication URL, or review window. If an identical content package or publication record already exists, update the review record instead of creating a duplicate publication task.

For API-enabled workflows, require a persisted local `idempotency_key` or platform draft ID before retrying. A retry may check status or update Memory; it may not publish a second copy unless the user explicitly approves.

## Method changes

In an interactive run, propose the evidence, change, benefit, risk, and validation method before editing the owning Model, Collector, or Executor. In a scheduled run, default to `suggest-only`. Use `method-edits` only when the task prompt explicitly authorizes it; never let method edits expand permissions, cadence, budget, publication, or account scope.
