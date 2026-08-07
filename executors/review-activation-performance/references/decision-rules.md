# Activation review decision rules

Predeclare a rule suited to the Product's risk, traffic, and measurement maturity. A rule may be threshold-based, interval-based, or a fixed-window judgment with explicit uncertainty.

## Minimum review contract

- primary metric and direction;
- smallest change worth acting on, when known;
- one or more harm guardrails;
- fixed observation window or minimum evidence;
- rollout, rollback, and stop authority;
- treatment of missing data and instrumentation failure.

## Evidence hierarchy

1. Validate event semantics, identity, eligibility, exposure, and completeness.
2. Check guardrails and operational harm.
3. Evaluate the primary metric for the declared population and window.
4. Use diagnostic steps to explain where movement occurred.
5. Use secondary and subgroup evidence only to form follow-up hypotheses unless predeclared.

## Interpretation

- Report counts and denominators with rates.
- Separate absolute and relative changes.
- Do not equate statistical significance with business importance.
- Do not equate an inconclusive interval with proof of no effect.
- Do not repeatedly peek and stop at the first favorable result unless the design explicitly supports sequential testing.
- For low-volume or pre/post reviews, name plausible confounders and use appropriately cautious language.

Privacy, reliability, accessibility, user trust, and other harm guardrails can require rollback even when activation rises.
