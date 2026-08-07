# Product activation loop automation

Use this reference only for recurring activation observation. Follow root `AUTOMATION.md`.

## Readiness

Do not schedule until the same observation scope has run manually and the event source, measurement contract, Memory output, comparison window, and permission boundary are verified.

Start in `Observe` mode. Product changes, deployments, experiment allocation, messaging, spending, and rollouts remain disabled until separately tested and authorized.

## Observation-only task template

```text
Run $run-product-activation-loop in observation-only mode for the current Product.

Read AGENTS.md, DATA.md, AUTOMATION.md, determine the Product workspace, then read its SOUL.md, the canonical activation Model, and relevant memory/run-product-activation-loop files.

For this run:
- use the latest compatible measurement contract and completed data window;
- compare only populations, event versions, identity rules, exclusions, and time windows that are genuinely comparable;
- use only authorized read-only sources and process supplied exports through $read-product-events;
- write a dated aggregate review to memory/run-product-activation-loop/ without row-level identifiers;
- distinguish no material change, incomplete data, instrumentation failure, and a real behavior change;
- if nothing decision-relevant changed, record that briefly and take no action;
- do not modify product code, deploy, allocate experiments, message users, spend money, or change credentials;
- use change policy suggest-only.
```

## Stop conditions

Stop and request user action when the event contract changed, identity or exposure assignment is invalid, the data window is incomplete, guardrails indicate harm, a source loses authorization, or the next action requires product or external-system modification.

Choose cadence from event latency, traffic, and the predeclared decision window. Do not repeatedly inspect an unchanged partial window.
