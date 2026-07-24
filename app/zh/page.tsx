import Link from 'next/link';
import { GrowthTrace } from '@/components/growth-trace';
import { JsonLd } from '@/components/json-ld';
import { githubUrl, getSiteUrl } from '@/lib/site';

export default function ChineseHomePage() {
  const siteUrl = `${getSiteUrl()}/zh`;
  return (
    <main>
      <JsonLd data={{
        '@context': 'https://schema.org', '@type': 'SoftwareApplication', name: 'Growth Lab',
        applicationCategory: 'BusinessApplication', operatingSystem: 'Codex 与 Claude Code 工作区',
        description: '由 Coding Agent 从代码到市场执行一切的开源端到端增长工具。',
        url: siteUrl, codeRepository: githubUrl,
        offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
      }} />

      <section className="home-hero">
        <div className="hero-copy">
          <span className="utility-label">开源增长 RUNTIME</span>
          <h1>让 Coding Agent <em>交付增长。</em></h1>
          <p>Growth Lab 帮助产品从代码走向市场。Codex 或 Claude Code 理解产品、发现需求、完成创作与执行、度量结果，并用每一次结果决定下一步。</p>
          <div className="button-row">
            <a className="button button-primary" href={githubUrl}>Clone on GitHub ↗</a>
            <Link className="button button-quiet" href="/zh/ai-seo-agent">查看 SEO 闭环</Link>
          </div>
          <code className="clone-line">git clone https://github.com/tsingyuai/growth-lab.git</code>
        </div>
        <GrowthTrace locale="zh" />
      </section>

      <section className="proof-strip" aria-label="SEO 闭环实测结果">
        <div><strong>1–2 天</strong><span>新页面被收录</span></div>
        <div><strong>+1000%</strong><span>页面曝光量</span></div>
        <div><strong>+1000%</strong><span>页面点击量</span></div>
        <div><strong>−50%</strong><span>7 天平均 CTR</span></div>
        <p>来自一次真实执行。CTR 的下降也会成为下一轮分析的输入。</p>
      </section>

      <section className="section thesis-section">
        <div><span className="section-code">理念 / 001</span><h2>产品本身就是 Brief。</h2></div>
        <div className="thesis-copy">
          <p>Coding Agent 已经能够读取代码仓库、浏览网络、操作工具、修改文件，并在会话中与你协作。</p>
          <p>Growth Lab 为这个 Runtime 提供可持续的增长方法：观察什么、采取什么行动、怎样执行，以及结果发生后应当记住什么。</p>
        </div>
      </section>

      <section className="section capability-section" id="capability">
        <div className="section-heading">
          <span className="section-code">现有能力 / LIVE</span>
          <h2>一个能力。<br />一个完整闭环。</h2>
          <p>每个能力都包含观察、行动、复盘与持久化记忆。</p>
        </div>
        <div className="capability-card">
          <div className="card-topline"><span>MODEL</span><span>run-seo-page-loop</span></div>
          <h3>SEO 页面增长闭环</h3>
          <p>思考用户在什么场景下可能会需要你的产品，调研这些场景中用户会实际搜索什么，生成具有信息量、能解决用户问题，并引流到产品的 SEO 页面。</p>
          <ol>
            <li><span>观察</span>用户场景、实时搜索结果与真实搜索需求</li>
            <li><span>行动</span>创作、审查、生图、发布并通知 IndexNow</li>
            <li><span>复盘</span>Bing 曝光、点击、查询词与产品结果</li>
            <li><span>记忆</span>持久化证据与下一步行动建议</li>
          </ol>
          <Link href="/zh/ai-seo-agent">了解闭环如何运行 →</Link>
        </div>
      </section>

      <section className="section zero-section">
        <span className="section-code">从零开始</span>
        <h2>还没有第一个客户，也足以开始。</h2>
        <div className="zero-grid">
          <div><strong>01</strong><h3>打开产品</h3><p>从代码仓库、原型、网址或一个产品想法开始。</p></div>
          <div><strong>02</strong><h3>让 Agent 观察</h3><p>它形成用户假设、采集市场证据，并建立或接入分析管线。</p></div>
          <div><strong>03</strong><h3>执行真实行动</h3><p>它交付工作、度量结果，并把下一次决策写入 Memory。</p></div>
        </div>
      </section>

      <section className="closing-cta">
        <span className="utility-label">代码 → 市场 → 记忆</span>
        <h2>在产品所在的地方运行增长。</h2>
        <p>Clone 仓库，在 Codex 或 Claude Code 中打开工作区，让 Growth Lab 理解你的产品并开始执行增长闭环。</p>
        <a className="button button-primary" href={githubUrl}>开始使用 Growth Lab ↗</a>
      </section>
    </main>
  );
}
