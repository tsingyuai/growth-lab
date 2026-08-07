---
name: review-social-performance
description: Review social content outcomes from platform exports, URLs, screenshots, traffic links, product events, and guardrails, then recommend the next action without overstating attribution. Use after Xiaohongshu notes, WeChat official account articles, or social content packages have been published or handed off.
---

# Review social performance

Evaluate the learning goal, not just the largest metric.

## Required evidence

Recover from the current Product workspace's `memory/run-social-content-loop/`:

- original content package and selected candidate;
- publication record and URL or not-published state;
- platform, account scope, publish time, format, and boost status;
- link, UTM, QR, referral, landing page, or campaign code;
- planned observation window and success/guardrail criteria;
- prior comparable campaigns when available.

Invoke `$read-social-platform-export` for authorized platform exports. Invoke `$read-product-events` for registration or activation exports when available.

## Validate

Check whether:

- platform metrics cover the complete window;
- boosted and organic metrics are separated;
- post IDs or URLs match the publication record;
- link/campaign parameters are present;
- product events use compatible definitions and time windows;
- negative comments, reports, unsubscribes, or support burden are visible enough to assess guardrails.

## Analyze

Separate:

- exposure/reach;
- reads/views;
- engagement: likes, comments, saves, shares, follows;
- traffic movement: clicks, landing visits, QR scans;
- product conversion: registrations or leads;
- activation or first-value events;
- guardrails and qualitative feedback.

Use counts before rates. State attribution strength: direct, plausible, weak, or unavailable.

## Decide

Choose one primary next action:

- continue collecting;
- create another variant;
- adapt to another platform;
- revise hook, asset, CTA, or landing path;
- improve measurement;
- pause topic;
- stop campaign;
- request authorization.

Write a dated review linked to the package, publication record, platform aggregate evidence, product aggregate evidence, limitations, and next action.
