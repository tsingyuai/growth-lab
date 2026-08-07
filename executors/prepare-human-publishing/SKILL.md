---
name: prepare-human-publishing
description: Prepare a human-assisted publishing package with final content, assets, target platform settings, timing, links, and step-by-step operating instructions while keeping account-sensitive actions with a person. Use for Xiaohongshu, WeChat, or other platforms when Growth Lab should not log in, upload, or publish automatically.
---

# Prepare human publishing

Create a complete handoff package. Do not log in, upload files, create drafts, publish, delete, boost, reply, or change account settings.

## Required inputs

Require a reviewed content package with decision `ready for human publishing` or a clearly approved equivalent.

## Handoff package

Include:

- target platform and account scope described by the user, not secret IDs;
- final title/body/card/article copy;
- asset list in upload order with filenames, dimensions, and notes;
- link, UTM, QR, referral, or landing-page instructions;
- tags, topics, excerpt, cover, and settings;
- suggested publish time and rationale when available;
- visible caveats or compliance notes that must not be removed;
- exact steps for a human to publish in the platform UI;
- what to return after publishing: URL, screenshots, publish time, account, and exported metrics later;
- idempotency note: do not publish again if the same URL or screenshot is already recorded.

Store the handoff in the current Product workspace's `memory/run-social-content-loop/` or the current package folder.

## Follow-up

Ask the human to provide the final URL or screenshot after publication. The next review can start only from a publication record or a clear "not published" state.
