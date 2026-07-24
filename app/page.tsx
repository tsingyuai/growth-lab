import Link from 'next/link';
import { GrowthTrace } from '@/components/growth-trace';
import { JsonLd } from '@/components/json-ld';
import { githubUrl, getSiteUrl } from '@/lib/site';

export default function HomePage() {
  const siteUrl = getSiteUrl();
  return (
    <main>
      <JsonLd data={{
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'Growth Lab',
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Codex and Claude Code workspaces',
        description: 'An open-source, end-to-end growth tool executed by coding agents from code to market.',
        url: siteUrl,
        codeRepository: githubUrl,
        offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
      }} />

      <section className="home-hero">
        <div className="hero-copy">
          <span className="utility-label">OPEN-SOURCE GROWTH RUNTIME</span>
          <h1>Your coding agent can <em>ship growth.</em></h1>
          <p>
            Growth Lab takes a product from code to market. Codex or Claude Code reads the product,
            finds demand, creates, executes, measures, and uses every result to decide what to do next.
          </p>
          <div className="button-row">
            <a className="button button-primary" href={githubUrl}>Clone on GitHub ↗</a>
            <Link className="button button-quiet" href="/ai-seo-agent">Explore the first loop</Link>
          </div>
          <code className="clone-line">git clone https://github.com/tsingyuai/growth-lab.git</code>
        </div>
        <GrowthTrace />
      </section>

      <section className="proof-strip" aria-label="Observed SEO loop result">
        <div><strong>1–2 days</strong><span>to index new pages</span></div>
        <div><strong>+1000%</strong><span>page impressions</span></div>
        <div><strong>+1000%</strong><span>page clicks</span></div>
        <div><strong>−50%</strong><span>7-day average CTR</span></div>
        <p>One observed run. The lower CTR became evidence for the next iteration.</p>
      </section>

      <section className="section thesis-section">
        <div>
          <span className="section-code">THESIS / 001</span>
          <h2>The product is the brief.</h2>
        </div>
        <div className="thesis-copy">
          <p>A coding agent already knows how to read repositories, browse the web, operate tools, edit files, and work with you in a session.</p>
          <p>Growth Lab gives that runtime durable growth methods: what to observe, which action to take, how to execute it, and what to remember after the result arrives.</p>
        </div>
      </section>

      <section className="section capability-section" id="capability">
        <div className="section-heading">
          <span className="section-code">CAPABILITY / LIVE</span>
          <h2>One capability.<br />One complete loop.</h2>
          <p>Each capability owns its observation, action, review, and persistent memory.</p>
        </div>
        <div className="capability-card">
          <div className="card-topline"><span>MODEL</span><span>run-seo-page-loop</span></div>
          <h3>SEO page growth loop</h3>
          <p>Think through when users may need your product, research what they actually search in those situations, then create useful pages that solve the problem and lead into the product.</p>
          <ol>
            <li><span>Observe</span> user scenarios, live SERPs, and real search demand</li>
            <li><span>Act</span> create, review, illustrate, publish, and notify IndexNow</li>
            <li><span>Review</span> Bing exposure, clicks, queries, and product outcomes</li>
            <li><span>Remember</span> preserve evidence and the next recommended action</li>
          </ol>
          <Link href="/ai-seo-agent">Read how the loop works →</Link>
        </div>
      </section>

      <section className="section zero-section">
        <span className="section-code">START / ZERO</span>
        <h2>No customers yet is enough context to begin.</h2>
        <div className="zero-grid">
          <div><strong>01</strong><h3>Open the product</h3><p>Start from a repository, prototype, URL, or product idea.</p></div>
          <div><strong>02</strong><h3>Let the agent observe</h3><p>It forms user hypotheses, collects market evidence, and connects analytics.</p></div>
          <div><strong>03</strong><h3>Run a real action</h3><p>It ships work, measures what happened, and writes the next decision to Memory.</p></div>
        </div>
      </section>

      <section className="closing-cta">
        <span className="utility-label">CODE → MARKET → MEMORY</span>
        <h2>Run growth where the product already lives.</h2>
        <p>Clone the repository. Open it in Codex or Claude Code. Ask Growth Lab to understand your product and start the first loop.</p>
        <a className="button button-primary" href={githubUrl}>Start with Growth Lab ↗</a>
      </section>
    </main>
  );
}
