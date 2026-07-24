import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl, languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: '面向 0→1 产品的 AI 营销 Agent',
  description: 'AI 营销 Agent 可以从产品想法或代码仓库开始，采集需求证据、执行增长工作、建立分析管线并复盘结果。',
  alternates: { canonical: '/zh/ai-marketing-agent', languages: languageAlternates('/ai-marketing-agent') },
  openGraph: { title: '面向 0→1 产品的 AI 营销 Agent', description: '从代码出发，采集证据、执行增长行动并从真实结果中学习。', url: '/zh/ai-marketing-agent', locale: 'zh_CN' },
};

export default function ChineseAiMarketingAgentPage() {
  const url = `${getSiteUrl()}/zh/ai-marketing-agent`;
  return <><JsonLd data={{ '@context': 'https://schema.org', '@type': 'Article', inLanguage: 'zh-CN', headline: '面向 0→1 产品的 AI 营销 Agent', dateModified: '2026-07-24', author: { '@type': 'Organization', name: 'Growth Lab' }, mainEntityOfPage: url }} />
    <SeoShell locale="zh" updated="2026 年 7 月 24 日" eyebrow="产品指南 / AI 营销 AGENT" title="AI 营销 Agent 可以在第一个客户出现之前开始工作。" intro="给它一个产品想法、代码仓库、原型或网址。它可以建立缺失的上下文，运行第一次增长行动，接入度量并从结果中学习。">
      <p>早期产品通常没有完整的营销 Brief，甚至没有客户、Campaign 历史、分析数据、定位或经过验证的理想用户画像。有效的 AI 营销 Agent 会把这些缺失本身作为第一次观察。</p>
      <h2>Agent 从 Day Zero 做什么</h2>
      <div className="decision-grid">
        <div><strong>理解产品</strong><span>读取代码、路由、文档、Onboarding、定价与现有产品表述。</span></div>
        <div><strong>形成假设</strong><span>描述可能的用户、使用场景、紧迫任务和能够推翻假设的信号。</span></div>
        <div><strong>采集证据</strong><span>调研真实搜索、社区、竞品、公开内容和可用的产品数据。</span></div>
        <div><strong>制造信号</strong><span>交付页面、Campaign、分发行动或实验，产生可观察的反馈。</span></div>
      </div>
      <h2>为什么代码仓库很重要</h2>
      <p>Coding Agent 可以直接检查产品，了解真实存在的功能、网站如何描述它们、激活发生在哪里、已经追踪了哪些事件，以及当前代码库中哪些内容可以修改。</p>
      <p>识别搜索机会的同一场会话可以创建路由、撰写页面、添加元数据、测试渲染、接入分析、通过现有工作流部署并检查结果。</p>
      <h2>首先自动化什么</h2>
      <table><thead><tr><th>闭环</th><th>观察</th><th>行动</th><th>复盘信号</th></tr></thead><tbody>
        <tr><td>SEO 页面</td><td>用户场景与搜索需求</td><td>创建并发布有用页面</td><td>收录、查询词、曝光、点击与产品行动</td></tr>
        <tr><td>版本分发</td><td>产品变化与相关受众</td><td>生成渠道化发布材料</td><td>触达、访问、注册与激活</td></tr>
        <tr><td>Onboarding</td><td>早期用户在哪里停止</td><td>修改一个关键决策</td><td>完成率与激活率</td></tr>
        <tr><td>内容学习</td><td>用户问题与高表现模式</td><td>创作并分发内容包</td><td>有效互动与产品行为</td></tr>
      </tbody></table>
      <h2>Agent 建立数据路径</h2>
      <p>用户提供产品和期望结果。Agent 检查现有埋点，添加事件、接入分析服务、导入已有数据，或建立适合当前阶段的轻量采集路径。真实用户到达后，第一方信号会逐步替代假设。</p>
      <h2>Growth Lab 如何组织 Agent</h2>
      <ul><li><strong>Model：</strong>观察—行动—复盘闭环。</li><li><strong>Collectors：</strong>获取证据的方法与 Clients。</li><li><strong>Executors：</strong>完成创作和执行的原则与工具。</li><li><strong>Memory：</strong>带时间的运营证据、结果与下一步建议。</li><li><strong>Runtime：</strong>控制所有工作的 Codex 或 Claude Code 会话。</li></ul>
    </SeoShell></>;
}
