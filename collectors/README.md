# Collectors / 数据采集器

Collectors connect the Coding Agent to growth intelligence. They provide ways to discover, retrieve, and inspect external signals and product-internal data.

数据采集器连接 Coding Agent 与增长情报，提供发现、获取和检查外部信号及产品内部数据的能力。

## Scope / 范围

- Demand intelligence / 需求情报
- Competitive intelligence / 竞品情报
- High-performing content / 爆款内容
- Product growth data / 产品内部增长数据

## What belongs here / 这里承载什么

- Thin Clients and CLIs for official APIs / 面向官方 API 的轻量 Client 与 CLI
- MCP integrations / MCP 集成
- Browser collection workflows / 浏览器采集工作流
- Instructions for reading exports, event data, interviews, and feedback / 读取数据导出、事件数据、访谈与反馈的指引
- Source-specific references required by an Agent / Agent 使用特定来源时需要的参考资料

Each collector should help the Agent obtain evidence for a concrete question. The Agent decides what to collect and how to organize the result in the current workspace.

每个采集器都应帮助 Agent 为具体问题获取证据。Agent 根据当前 workspace 与任务决定采集什么，以及如何组织结果。

Use official APIs, authorized access, public sources, and user-provided data. Follow platform terms, privacy requirements, copyright rules, and source-specific rate limits.

使用官方 API、已授权访问、公开来源和用户提供的数据，并遵守平台条款、隐私要求、版权规则与来源侧速率限制。

## Available collectors / 已有采集器

- [`bing-webmaster/`](bing-webmaster/)：读取关键词热度、页面搜索表现、查询表现与 URL 索引信息。
- [`research-seo-demand`](research-seo-demand/SKILL.md)：扩展关键词族、验证热度、研究实时 SERP 并选择 SEO 页面机会。
- [`research-product`](research-product/SKILL.md)：在真实 loop 中渐进研究产品，并把稳定认知增量写入 `SOUL.md`。
- [`xiaohongshu-mcp`](xiaohongshu-mcp/SKILL.md)：通过本机 browser-first 服务只读搜索小红书、下载视觉候选并脱敏归档，首次默认推荐 25 条。
- [`media-crawler`](media-crawler/SKILL.md)：统一安装、认证、配置、运行和诊断其他平台使用的外部 MediaCrawler。
- 其他平台方法论：[`抖音`](media-crawler-douyin/SKILL.md) · [`快手`](media-crawler-kuaishou/SKILL.md) · [`B站`](media-crawler-bilibili/SKILL.md) · [`微博`](media-crawler-weibo/SKILL.md) · [`贴吧`](media-crawler-tieba/SKILL.md) · [`知乎`](media-crawler-zhihu/SKILL.md)。
