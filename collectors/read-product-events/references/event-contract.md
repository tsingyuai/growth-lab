# Product event contract

Confirm this contract before interpreting an activation funnel.

## Meaning

- **Journey start:** the event or cohort condition that makes an entity eligible.
- **Diagnostic steps:** ordered milestones used to locate friction. They need not all represent value.
- **Activation:** the first event that demonstrates the Product's intended value for this journey.
- **Entity:** user or account by default; use device or session only when that is the actual decision unit.
- **Window:** maximum elapsed time from journey start to activation.
- **Population:** included acquisition sources, platforms, locales, plans, versions, and dates.

## Identity

Document anonymous and authenticated identifiers, merge behavior, account membership, cross-device limitations, and deletion handling. Do not combine identifiers merely because values look similar.

## Event quality

For every required event, confirm:

- canonical name and version;
- exact firing condition and whether it can fire more than once;
- client or server origin;
- timestamp timezone and delivery latency;
- required properties and allowed values;
- staff, test, bot, retry, and duplicate treatment;
- release that introduced or changed the event.

## Comparison safety

Do not compare funnels when event semantics, identity rules, population, exclusions, or activation windows differ materially. Version a changed contract and retain both definitions in the owning Model Memory.

An analytics event is evidence that instrumentation emitted a record. It is not by itself proof that the user perceived value or that the data arrived exactly once.
