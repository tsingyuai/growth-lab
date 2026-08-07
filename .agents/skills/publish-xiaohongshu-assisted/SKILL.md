---
name: publish-xiaohongshu-assisted
description: Use Growth Lab's Xiaohongshu publishing Executor for human-assisted packages or separately approved publication through the configured local xiaohongshu-mcp browser runtime.
---

# Publish Xiaohongshu assisted

1. Read `../../../executors/publish-xiaohongshu-assisted/SKILL.md` completely.
2. Default to human-assisted publishing.
3. Treat xiaohongshu-mcp publication as authorized browser automation, not an official Xiaohongshu API.
4. Read-only login is not publication approval. Require the exact package hash and a current explicit confirmation; never retry an ambiguous result.
