---
name: read-webmaster-export
description: Inspect, normalize, validate, and interpret user-provided webmaster CSV or JSON exports for SEO demand and performance analysis without an API key. Use when reading query, page, impression, click, CTR, position, index, device, country, or date-range exports from Bing Webmaster, Google Search Console, or another webmaster platform.
---

# Read webmaster exports

Treat the export as time-scoped evidence, not a complete analytics truth.

## Establish provenance

Record:

- source platform and site property;
- export time and analysis date range;
- filters, search type, country, device, and timezone when known;
- whether rows represent queries, pages, query-page pairs, dates, or index status;
- whether privacy thresholds or row limits may hide data.

Ask only for missing information that changes interpretation.

## Inspect safely

- Read CSV or JSON without modifying the source file.
- For common tabular exports, run `python collectors/read-webmaster-export/normalize_webmaster_export.py <input> --source <platform> --site <property>`. Add `--date-from`, `--date-to`, and `--out` when known.
- Treat the script output as normalization evidence, not a finished analysis. Review its field map and warnings before interpreting rows.
- Keep private raw exports in the team's chosen private Memory or data location.
- Do not copy credentials, personal information, or unnecessary raw rows into shared Markdown.
- Preserve the source column names in a short field map.

## Normalize meaning

Map fields by meaning rather than exact spelling:

| Meaning | Common fields |
|---|---|
| Query | query, keyword, 搜索词, 关键词 |
| Page | page, url, landing page, 页面 |
| Impressions | impressions, impression, 展现, 曝光 |
| Clicks | clicks, click, 点击 |
| CTR | ctr, click through rate, 点击率 |
| Position | position, average position, 平均排名 |
| Date | date, day, 日期 |
| Country/device | country, device, 国家, 设备 |
| Index status | status, index status, coverage state, 索引状态, 收录状态 |

Do not silently combine rows with different search types, filters, date windows, countries, devices, or aggregation levels.

## Validate

Check:

- required dimensions and metrics exist for the current question;
- dates parse and the window is complete;
- numeric fields use consistent units and decimal conventions;
- CTR approximately matches clicks divided by impressions when aggregation permits;
- URLs are normalized carefully without merging distinct canonical pages;
- totals are not double-counted across query, page, and query-page exports;
- missing or zero values are distinguished from unavailable data.

Report schema or quality problems before drawing conclusions.

## Interpret for the task

Produce only the views needed by the calling task, such as:

- leading and emerging queries;
- pages gaining or losing visibility;
- high-impression, low-CTR opportunities;
- ranking bands and movement;
- query-page intent mismatch;
- new-page discovery and index evidence;
- comparable-period changes.

Separate observations from interpretation. Account for launch dates, incomplete windows, seasonality, branded queries, and small denominators.

## Return evidence

Return:

- provenance and data-quality limits;
- normalized field map;
- task-specific aggregates or tables;
- supported findings and confidence;
- missing evidence;
- the smallest next collection or analysis step.

Do not claim product conversion from webmaster data alone. Link page-level search evidence to separately collected product events when available.
