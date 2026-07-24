import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl, languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: 'Agentic Marketing：可执行的增长工作模型',
  description: '面向 0→1 产品的免费开源 Agentic Marketing 系统，自己理解产品与客户，完成调研、执行、度量和复盘。',
  alternates: { canonical: '/zh/agentic-marketing', languages: languageAlternates('/agentic-marketing') },
  openGraph: { title: 'Agentic Marketing：可执行的增长工作模型', description: '建立能够观察、行动、复盘并记忆的营销闭环。', url: '/zh/agentic-marketing', locale: 'zh_CN' },
};

export default function ChineseAgenticMarketingPage() {
  const url = `${getSiteUrl()}/zh/agentic-marketing`;
  return <><JsonLd data={{ '@context': 'https://schema.org', '@type': 'Article', inLanguage: 'zh-CN', headline: 'Agentic Marketing：可执行的增长工作模型', dateModified: '2026-07-24', author: { '@type': 'Organization', name: 'Growth Lab' }, mainEntityOfPage: url }} />
    <SeoShell locale="zh" updated="2026 年 7 月 24 日" eyebrow="实践指南 / AGENTIC MARKETING" title="Agentic Marketing 能把产品从 0 带到 1。" intro="Growth Lab 让 Codex 或 Claude Code 理解产品、发现客户、执行增长、度量结果并持续行动。它免费开源，所有交互都在一场对话中完成。">
      <p>Agentic Marketing 把市场洞察和执行经验转化为 AI Agent 能自己应用的指令。Growth Lab 从代码仓库、原型、URL 或想法开始，建立缺失的产品与客户上下文，选择工具，完成工作，检查结果，并为下一轮保留证据。</p>
      <h2>一个可工作的营销 Agent 包含五部分</h2>
      <table><thead><tr><th>环节</th><th>关键问题</th><th>示例</th></tr></thead><tbody>
        <tr><td>观察</td><td>市场或产品发生了什么变化？</td><td>新的搜索词开始触达页面。</td></tr>
        <tr><td>决策</td><td>证据支持哪一个行动？</td><td>围绕到达的意图重写标题。</td></tr>
        <tr><td>执行</td><td>哪些工具能够完成行动？</td><td>修改元数据、测试、部署并提交 IndexNow。</td></tr>
        <tr><td>复盘</td><td>行动之后发生了什么？</td><td>比较曝光、排名、CTR 与激活。</td></tr>
        <tr><td>记忆</td><td>下一轮需要知道什么？</td><td>时间、证据、行动、结果与建议。</td></tr>
      </tbody></table>
      <h2>从一个狭窄闭环开始</h2>
      <p>狭窄闭环拥有可识别的观察、Agent 能触达的行动面，以及能在有用时间内出现的结果。SEO 页面、版本发布、Onboarding 分析和内容再利用都可以分别成为一个闭环。</p>
      <pre><code>{`读取 Memory
→ 观察一个信号
→ 选择一个行动
→ 调用所需工具
→ 检查执行结果
→ 等待外部结果
→ 复盘并写入 Memory`}</code></pre>
      <h2>Agent 需要访问什么</h2>
      <h3>产品</h3><p>仓库访问让 Coding Agent 看到真实的功能、路由、Onboarding、内容、分析埋点与限制。更早期的产品也可以从 URL、原型或想法开始。</p>
      <h3>外部世界</h3><p>搜索与浏览器能力负责市场观察，官方 API、数据导出和授权 Clients 提供结构化数据或外部行动，凭据保存在环境变量中。</p>
      <h3>持久化结果的位置</h3><p>Memory 保存按时间记录的运营证据和下一步行动。闭环方法保留在 Skill 中，团队能够直接检查和改进。</p>
      <h2>会话就是控制面</h2>
      <p>Codex 或 Claude Code 会话读取 Skills、使用原生浏览器与编码工具、调用 Clients、修改工作区，并在需要权限或判断时与人协作。</p>
      <p>安装过程就是 Clone，交互方式就是在 Codex 或 Claude Code 中对话。无需学习独立看板、注册新的 SaaS 账号或维护大量 Campaign 配置。</p>
    </SeoShell></>;
}
