import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl } from '@/lib/site';

export const metadata: Metadata = {
  title: 'AI Marketing Tools: Choose by the Work You Need Done',
  description: 'A practical framework for choosing AI marketing tools by product context, execution depth, feedback, and the growth work your team needs completed.',
  alternates: { canonical: '/ai-marketing-tools' },
  openGraph: { title: 'AI Marketing Tools: Choose by the Work You Need Done', description: 'Compare AI marketing tools by the work they can observe, execute, and learn from.', url: '/ai-marketing-tools' },
};

export default function AiMarketingToolsPage() {
  const url = `${getSiteUrl()}/ai-marketing-tools`;
  return (
    <>
      <JsonLd data={{ '@context': 'https://schema.org', '@type': 'Article', headline: 'AI Marketing Tools: Choose by the Work You Need Done', dateModified: '2026-07-24', author: { '@type': 'Organization', name: 'Growth Lab' }, mainEntityOfPage: url }} />
      <SeoShell eyebrow="BUYER GUIDE / AI MARKETING TOOLS" title="Choose an AI marketing tool by the work it can finish." intro="The useful dividing line is execution depth: how much product context the tool can read, which actions it can complete, and whether results change its next decision.">
        <p>“AI marketing tool” now describes products with very different jobs. A writing assistant drafts. An automation platform routes events. A specialist product operates one channel. A coding agent can read the product, connect tools, modify assets, and work across the full repository.</p>

        <blockquote>Start with the growth job. Choose the smallest tool that can observe the right evidence, complete the action, and return a measurable result.</blockquote>

        <h2>Four categories of AI marketing tools</h2>
        <table>
          <thead><tr><th>Category</th><th>Best at</th><th>Context</th><th>Execution</th><th>Feedback</th></tr></thead>
          <tbody>
            <tr><td>General AI assistant</td><td>Ideas, drafts, summaries</td><td>Prompt and attached files</td><td>Produces an answer</td><td>Depends on the next prompt</td></tr>
            <tr><td>Marketing automation</td><td>Known event-driven journeys</td><td>CRM and campaign fields</td><td>Runs configured rules</td><td>Dashboards and reports</td></tr>
            <tr><td>Specialist AI tool</td><td>One channel or artifact</td><td>Channel-specific inputs</td><td>Creates or optimizes within its product</td><td>Channel metrics</td></tr>
            <tr><td>Coding-agent growth workspace</td><td>Crossing product, market, content, and data</td><td>Repository, web, files, and connected tools</td><td>Researches, creates, edits, calls tools, and measures</td><td>Persistent Memory informs the next action</td></tr>
          </tbody>
        </table>

        <h2>Match the tool to your actual constraint</h2>
        <div className="decision-grid">
          <div><strong>You need more output</strong><span>Choose a focused creation tool with strong review controls.</span></div>
          <div><strong>You know the journey</strong><span>Choose automation with reliable triggers, identity, and delivery.</span></div>
          <div><strong>You need to find demand</strong><span>Choose a system that can research live markets and connect findings to product action.</span></div>
          <div><strong>You are pre-traction</strong><span>Choose a system that begins from code and hypotheses, then helps create the first data pipeline.</span></div>
        </div>

        <h2>What to evaluate before adopting a tool</h2>
        <h3>1. Product context</h3>
        <p>Check whether the tool can understand the product beyond a brand prompt. For a technical product, useful context includes routes, features, onboarding, pricing logic, documentation, event names, and existing content.</p>

        <h3>2. Action surface</h3>
        <p>List the actions the tool can really complete: edit a page, generate an asset, publish through an authorized API, inspect a live result, or analyze exported metrics. Separate executed actions from recommendations.</p>

        <h3>3. Evidence quality</h3>
        <p>A useful growth system distinguishes a source, an observation, a hypothesis, and a creative choice. Look for citations, access to first-party data, and a way to inspect the raw evidence behind a decision.</p>

        <h3>4. Learning across runs</h3>
        <p>Ask what the next session knows about the last one. A durable loop preserves dated operational evidence, the action taken, the observed result, and the next recommendation.</p>

        <h3>5. Control and portability</h3>
        <p>Local files and readable Skills make methods inspectable. Standard Clients and environment-managed credentials let teams replace external services without rewriting the growth method.</p>

        <h2>Where Growth Lab fits</h2>
        <p>Growth Lab is an open-source growth workspace for Codex and Claude Code. The coding agent is the runtime. Skills teach it how to run a complete growth loop. Clients provide external actions. Files preserve Memory.</p>
        <p>Its first working capability is an SEO page loop: discover situations in which users need the product, validate what they search, create useful pages, publish, measure Bing outcomes, and use the result to choose the next action.</p>

        <div className="note-box"><strong>Observed result</strong>In one Growth Lab run, new pages were indexed in 1–2 days. On a 7-day average, page impressions and clicks each increased 1000%, while overall CTR decreased 50%. The expanded reach and lower CTR became separate inputs for the next review.</div>

        <h2>A practical selection exercise</h2>
        <ol>
          <li>Write one growth outcome and the evidence that would prove it.</li>
          <li>List the product and market context required to choose an action.</li>
          <li>List every tool the action must call.</li>
          <li>Choose where a human must contribute access or judgment.</li>
          <li>Define what the next run needs to remember.</li>
        </ol>
        <p>The resulting list gives you a concrete tool requirement. It also reveals whether you need a writer, an automation platform, a channel specialist, or an agentic growth workspace.</p>
      </SeoShell>
    </>
  );
}
