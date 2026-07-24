import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl, languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: 'AI 营销工具：按真正要完成的工作选择',
  description: '免费开源的 AI 增长工具，自己理解产品与客户，通过 Codex 或 Claude Code 端到端执行产品 0→1 增长。',
  alternates: { canonical: '/zh/ai-marketing-tools', languages: languageAlternates('/ai-marketing-tools') },
  openGraph: { title: 'AI 营销工具：按真正要完成的工作选择', description: '比较不同 AI 营销工具能够观察、执行和学习的工作深度。', url: '/zh/ai-marketing-tools', locale: 'zh_CN' },
};

export default function ChineseAiMarketingToolsPage() {
  const url = `${getSiteUrl()}/zh/ai-marketing-tools`;
  return <><JsonLd data={{ '@context': 'https://schema.org', '@type': 'Article', inLanguage: 'zh-CN', headline: 'AI 营销工具：按真正要完成的工作选择', dateModified: '2026-07-24', author: { '@type': 'Organization', name: 'Growth Lab' }, mainEntityOfPage: url }} />
    <SeoShell locale="zh" updated="2026 年 7 月 24 日" eyebrow="选型指南 / AI 营销工具" title="选择能把产品从 0 带到 1 的 AI 营销工具。" intro="Growth Lab 免费开源，自己理解产品、调研客户与需求、端到端完成执行，并直接运行在你已经使用的 Codex 或 Claude Code 中。">
      <p>“AI 营销工具”覆盖了完全不同的工作。Growth Lab 面向完整的 0→1 路径：Coding Agent 读取产品，形成客户假设，采集实时市场证据，创作并发布增长资产，再从结果中学习。用户只需要提供产品和目标，市场洞察与执行方法由 Skills 提供。</p>
      <blockquote>先明确增长任务，再选择能够观察正确证据、完成行动并返回可度量结果的最小工具。</blockquote>
      <h2>四类 AI 营销工具</h2>
      <table><thead><tr><th>类别</th><th>擅长工作</th><th>上下文</th><th>执行方式</th></tr></thead><tbody>
        <tr><td>通用 AI 助手</td><td>想法、草稿、总结</td><td>Prompt 与附件</td><td>生成答案</td></tr>
        <tr><td>营销自动化</td><td>已知的事件驱动流程</td><td>CRM 与 Campaign 字段</td><td>运行配置规则</td></tr>
        <tr><td>垂直 AI 工具</td><td>单个渠道或内容资产</td><td>渠道特定输入</td><td>在产品内生成或优化</td></tr>
        <tr><td>Coding Agent 增长工作区</td><td>连接产品、市场、内容与数据</td><td>仓库、网络、文件与工具</td><td>调研、创作、修改、调用工具并度量</td></tr>
      </tbody></table>
      <h2>先匹配真正的限制条件</h2>
      <div className="decision-grid">
        <div><strong>需要更多内容产出</strong><span>选择具有明确审查机制的专业创作工具。</span></div>
        <div><strong>已经知道用户旅程</strong><span>选择触发、身份识别与送达可靠的自动化工具。</span></div>
        <div><strong>需要发现市场需求</strong><span>选择能调研实时市场并把发现连接到产品行动的系统。</span></div>
        <div><strong>产品尚未获得 Traction</strong><span>选择能从代码和假设开始，并帮助建立第一条数据管线的系统。</span></div>
      </div>
      <h2>采用之前检查什么</h2>
      <h3>产品上下文</h3><p>确认工具能否理解品牌 Prompt 之外的产品，包括路由、功能、Onboarding、定价、文档、事件名称和现有内容。</p>
      <h3>行动范围</h3><p>列出它能真正完成的操作：修改页面、生成资产、通过授权 API 发布、检查线上结果或分析数据。把已执行的行动与建议区分开。</p>
      <h3>证据与跨轮次学习</h3><p>有用的系统会区分来源、观察、假设和创作选择，并保存带时间的证据、行动、结果与下一步建议。</p>
      <h2>Growth Lab 所在的位置</h2>
      <p>Growth Lab 是面向 Codex 与 Claude Code 的免费开源增长工作区。Coding Agent 是 Runtime，Skills 提供市场分析与执行方法，Clients 提供外部行动，文件保存 Memory。Clone 仓库、在已有的 Coding Agent 中打开，然后描述目标即可开始。</p>
      <div className="note-box"><strong>实测结果</strong>一次真实执行中，新页面在 1–2 天内被收录；7 天平均曝光量与点击量分别提高 1000%，整体 CTR 降低 50%。扩大后的触达与降低的 CTR 会分别进入下一次复盘。</div>
    </SeoShell></>;
}
