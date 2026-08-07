# Activation experiment design

Use an experiment only when it can answer the current decision better than a staged rollout, usability study, instrumentation repair, or careful pre/post observation.

## Contract

Define before implementation:

- experiment unit and stable assignment key;
- eligibility and exclusion rules;
- control and treatment behavior;
- exposure event and exact firing boundary;
- primary activation metric and allowed window;
- guardrail metrics and rollback thresholds;
- minimum evidence or fixed review date;
- concurrent experiments and mutual-exclusion rules;
- owner and stop authority.

## Implementation rules

- Randomize only eligible entities and preserve assignment across sessions.
- Analyze assigned entities by assignment after valid exposure unless a predeclared design says otherwise.
- Keep allocation independent of user outcome and downstream behavior.
- Avoid changing the metric definition, population, allocation, or review window after observing results.
- Do not expose users to material risk merely to preserve a test. Stop when privacy, safety, reliability, or trust guardrails fail.

## Low traffic

Do not hide low power behind a significance label. Use a staged rollout, qualitative task observation, support evidence, latency/error data, or a longer fixed window. State which conclusions remain unavailable.

## Rollback

Prefer a server-controlled flag or existing release mechanism. Define how assignment, data interpretation, and partially completed user state behave after rollback.
