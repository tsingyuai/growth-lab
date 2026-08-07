# Social platform policy boundaries

Use this reference before preparing publication, upload, API draft creation, or live publishing.

## Common rules

- Use public sources, user-provided files, official APIs, or authorized account exports.
- Treat platform login, upload, draft creation, live publishing, deletion, paid boosting, comment replies, direct messages, and account settings as separate external actions.
- Ask for explicit approval before each external action category.
- Do not ask for or print credentials. Clients read credentials only from environment variables or approved local secret mechanisms.
- Store final public content and redacted aggregates in Memory. Store sensitive exports and raw account data only in the team's approved private path.
- In normal modes, do not copy competitor wording, screenshots, visual identity, unique examples, templates, or proprietary assets. In explicitly confirmed `close-replication`, one primary reference may supply a 1:1 card-order and layout map, but source wording, images, logos, people, proprietary UI, and brand assets must still be replaced and documented.

## Xiaohongshu

Default mode remains human-assisted publishing. The repository also exposes an explicitly approved browser-automation path through the configured `xpzouying/xiaohongshu-mcp` local service:

- prepare title, note body, tags, cover/card images, image order, alt/description notes, landing link or comment CTA, timing suggestion, and operating instructions;
- ask a human to publish through the normal Xiaohongshu interface;
- request the final note URL, screenshots, and exported metrics for review.

Do not describe that browser path as an official Xiaohongshu API. Collection login does not authorize upload or publication. The exact package hash, target account, visibility, schedule and a current `--confirm-publish` are required, and ambiguous outcomes stop without retry.

When an official authorized Client exists, keep upload/stage media, draft creation, live publication, metric query, deletion, comments, messages, and paid promotion as separate scopes.

## WeChat official account

WeChat official account can support official API workflows when the account and app permissions are authorized. Prefer the safest useful step first:

- prepare article package;
- upload or select media;
- create or update draft;
- preview to human reviewers;
- publish or mass-send only after separate approval;
- collect article and user engagement metrics through official export/API when authorized.

Treat draft creation as different from live publication. Do not mass-send, publish, delete, or modify account settings merely because draft creation was approved.

## Platform adaptation

Xiaohongshu usually requires fast-scanning title options, visual cards, save/comment triggers, topic tags, mobile-first text density, and clear boundaries around claims.

WeChat usually requires a stronger title/opening, article structure, source attribution, image placement, excerpt, reading flow, and a more durable reference value.

Use platform norms as format constraints, not as permission to exaggerate, copy viral formulas, or bury required caveats.
