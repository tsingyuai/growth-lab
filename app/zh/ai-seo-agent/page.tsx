import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl, languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: 'AI SEO Agent：从用户场景到可度量页面',
  description: '免费开源的 AI SEO Agent，自己理解产品和客户，端到端完成调研、创作、发布与 SEO 效果复盘。',
  alternates: { canonical: '/zh/ai-seo-agent', languages: languageAlternates('/ai-seo-agent') },
  openGraph: { title: 'AI SEO Agent：从用户场景到可度量页面', description: '在产品工作区中执行完整的 SEO 页面增长闭环。', url: '/zh/ai-seo-agent', locale: 'zh_CN' },
};

export default function ChineseAiSeoAgentPage() {
  const url = `${getSiteUrl()}/zh/ai-seo-agent`;
  const steps = ['理解产品场景', '调研真实搜索', '分析领先页面', '创作并审查页面', '部署并提交 IndexNow', '复盘 Bing 与产品结果'];
  return <><JsonLd data={{ '@context': 'https://schema.org', '@type': 'HowTo', inLanguage: 'zh-CN', name: '运行 AI SEO 页面增长闭环', description: '用 Coding Agent 调研、创作、发布、度量并迭代 SEO 页面。', dateModified: '2026-07-24', mainEntityOfPage: url, step: steps.map((name, index) => ({ '@type': 'HowToStep', position: index + 1, name })) }} />
    <SeoShell locale="zh" updated="2026 年 7 月 24 日" eyebrow="现有能力 / AI SEO AGENT" title="让 AI SEO Agent 运行完整的页面增长闭环。" intro="Growth Lab 理解产品、发现客户场景、调研真实搜索、创作并发布有效页面，再复盘 Bing 结果。它免费开源，直接运行在 Codex 或 Claude Code 中。">
      <p>一张 SEO 页面需要解决真实用户场景，并自然地把用户引向产品。Agent 从产品出发，自己完成市场工作：形成客户假设、发现潜在需求场景、验证用户使用的搜索语言，再直接在真实代码库中创建页面。</p>
      <h2>完整的 SEO 页面闭环</h2>
      <ol>
        <li><strong>读取 Memory。</strong>恢复产品或查询词族过去的观察、行动、结果与建议。</li>
        <li><strong>观察需求。</strong>扩展关键词族，在可用时验证 Bing 需求，并用 Runtime 浏览器检查实时 SERP。</li>
        <li><strong>选择一个页面。</strong>要求存在可观察需求、稳定意图、产品契合、有价值的信息缺口和可信的产品结果。</li>
        <li><strong>创作。</strong>匹配有效页面形态，增加原创证据与实用材料，实现元数据、结构化数据和相关图片。</li>
        <li><strong>对抗式审查。</strong>执行删除、反转、标题替换、去品牌、证据、图文与转化测试。</li>
        <li><strong>发布。</strong>运行产品检查、观察渲染页面、部署并通过 IndexNow 提交线上 URL。</li>
        <li><strong>复盘结果。</strong>比较抓取状态、查询词、曝光、排名、点击、CTR 与相关产品行为。</li>
        <li><strong>写入 Memory。</strong>保存证据、结论、观察结果与下一步行动建议。</li>
      </ol>
      <h2>Agent 如何发现页面机会</h2>
      <p>Agent 从用户可能需要产品的场景开始，沿概念、行动、工具、资源、竞品和问题扩展表达，再用自动补全、相关搜索、SERP、社区、评论和客服语言找到用户已经使用的词。</p>
      <h2>什么让页面值得被收录</h2>
      <ul><li><strong>搜索层：</strong>标题、描述、Heading、Canonical、结构化数据、内链与新鲜度。</li><li><strong>用户层：</strong>可见信息顺序、任务完成、信任、有效图片与转化路径。</li><li><strong>质量层：</strong>独有信息、具体数据、来源、作者、原创性与真实投入。</li></ul>
      <p>新页面通过流程、示例、质量标准、真实产品证据、原创分析、可复制材料、第一方来源或有效限制来填补信息缺口。</p>
      <h2>真实执行中的观察结果</h2>
      <table><thead><tr><th>信号</th><th>观察变化</th><th>进入下一轮的判断</th></tr></thead><tbody>
        <tr><td>收录</td><td>新页面在 1–2 天内被收录</td><td>本次发现路径有效</td></tr>
        <tr><td>曝光</td><td>7 天平均 +1000%</td><td>页面触达了更多搜索</td></tr>
        <tr><td>点击</td><td>7 天平均 +1000%</td><td>扩大的触达带来了更多访问</td></tr>
        <tr><td>整体 CTR</td><td>7 天平均 −50%</td><td>需要分别诊断查询词组合与摘要匹配</td></tr>
      </tbody></table>
      <h2>在你的产品中运行</h2>
      <pre><code>{`git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab

# 在 Codex 或 Claude Code 中打开工作区
# 使用产品路径或 URL 调用 run-seo-page-loop`}</code></pre>
      <p>Growth Lab 免费开源。Clone 仓库、在 Codex 或 Claude Code 中打开工作区、描述产品与目标即可开始；Coding Agent 的会话就是全部操作界面。</p>
    </SeoShell></>;
}
