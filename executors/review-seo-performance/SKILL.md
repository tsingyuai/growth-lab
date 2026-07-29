---
name: review-seo-performance
description: 使用 Bing Webmaster 页面与查询数据、索引状态、产品结果和 Bing AI Performance 证据复盘 SEO 页面，诊断收录、排名、点击率、意图、内容、转化和 AI 引用问题。需要比较周期表现、分析 citations、cited pages、grounding queries、query fan-out 或决定下一步 SEO/GEO 行动时使用。
---

# 复盘 SEO 与 AI 可见性

用可比较周期和页面原始目标复盘已发布页面。考虑上线日期、季节性、抓取与收录延迟，把证据与解释分开。

## 收集传统搜索证据

```bash
node collectors/bing-webmaster/bing-webmaster.mjs page-stats \
  --site "$SITE_URL" --out <page-stats-file>

node collectors/bing-webmaster/bing-webmaster.mjs page-query-stats \
  --site "$SITE_URL" --page "$PAGE_URL" --out <query-stats-file>

node collectors/bing-webmaster/bing-webmaster.mjs url-info \
  --site "$SITE_URL" --url "$PAGE_URL"
```

读取：

- 抓取与索引状态；
- 展现、查询、点击和点击率；
- 平均展现位置与点击位置；
- 页面或摘要更新前后的变化；
- 产品动作、激活、收入或当前产品真正关心的结果；
- 相关 Memory 中的基线和历史行动。

## 收集 Bing AI Performance

Bing Webmaster Tools 的 AI Performance 主要通过网页界面提供。使用已登录浏览器读取：

| 指标 | 含义 |
|---|---|
| Total Citations | 页面内容在 AI 答案中作为来源出现的总次数 |
| Cited Pages | 被 AI 当作来源的页面数量与时间变化 |
| Page-level citations | 具体 URL 的被引用次数 |
| Grounding Queries | AI 为寻找引用材料实际运行的检索短语 |

Grounding queries 与传统人类关键词不同。用户的一句话会被模型拆成多个查询，这就是 query fan-out。程序化查询常出现比较、评估、监控、标准、优缺点等结构，它们可以揭示传统关键词工具看不到的内容需求。

AI Performance 的产品状态和字段可能变化，grounding queries 没有稳定 API 时以 Bing Webmaster Tools 当前网页界面为准。只报告界面实际提供的数据，不把推测的合作方覆盖范围写成官方承诺。

### 用 Grounding queries 反推内容

1. 聚合重复出现的概念、对象、比较维度和任务。
2. 区分自然查询与程序化查询。
3. 找出频繁触发检索但当前页面引用弱或没有覆盖的概念。
4. 判断它应成为现有页面的新段落、比较表、FAQ、独立页面还是不值得处理的旁支。
5. 回到实时 SERP 和产品能力验证，不因 AI 查询出现就自动创建页面。

### 检查可提取性

- 高频 grounding 术语是否出现在对应 H2 与前一到两段；
- 结论是否前置，段落能否独立理解；
- 表格、FAQ、步骤和定义是否便于准确抽取；
- 数据、示例和来源是否足以支撑引用；
- 页面是否有作者、更新时间和相邻主题覆盖；
- schema.org、canonical、robots、sitemap 与 IndexNow 是否正确。
- 站点需要面向 LLM 提供内容导航时，检查 `llms.txt` 是否准确、可访问并只声明真实公开内容；不要把它当成收录或引用保证。

### 三层验证

1. 服务器日志：区分 BingBot、OAI-SearchBot 等机器访问和真实用户访问。
2. 查询模式：比较传统搜索查询与 AI Performance 的程序化 grounding queries。
3. 产品结果：把引用和搜索可见性与分析工具中的来源、访问和产品动作对照。

引用多、点击少不等于失败，也不等于成功。它表示内容被 AI 使用但没有形成等量访问，需要结合品牌呈现、用户后续动作和产品目标判断。

## 诊断主要约束

- 发现：目标 canonical 尚未被抓取或收录。
- 需求：目标词族没有足够可观察需求。
- 排名：有展现但位置弱。
- 摘要：位置有竞争力但点击率弱。
- 意图：实际到达查询与页面任务偏离。
- 内容：竞品提供更强证据、工具、信息增益、新鲜度或清晰度。
- 转化：页面满足搜索意图但没有带来相应产品行动。
- 有引用无访问：AI 系统使用内容，但用户很少继续访问或识别品牌。

## 输出复盘

需要视觉比较时，在当前 Model 的 Memory 生成独立 HTML，包含适合当前证据的周期比较、查询表、位置分布、产品结果、AI 引用、grounding query 分类和标注结论。原始导出放在同一 Memory 下。

推荐一个首要下一步，并说明验证它的证据：

- 加强当前页面；
- 修改 title 和摘要；
- 补充缺失证据、工具或信息增益；
- 调整转化路径；
- 新建支持页面；
- 修复收录、canonical 或发现问题；
- 增强 AI 可提取性；
- 等待一个明确观察窗口。
