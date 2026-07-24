import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl, languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: 'AI Marketing Agent for Products at Day Zero',
  description: 'A free, open-source AI marketing agent that understands the product and customers, then executes the complete 0→1 growth loop in Codex or Claude Code.',
  alternates: { canonical: '/ai-marketing-agent', languages: languageAlternates('/ai-marketing-agent') },
  openGraph: { title: 'AI Marketing Agent for Products at Day Zero', description: 'Start from code, collect evidence, execute growth actions, and learn from real outcomes.', url: '/ai-marketing-agent' },
};

export default function AiMarketingAgentPage() {
  const url = `${getSiteUrl()}/ai-marketing-agent`;
  return (
    <>
      <JsonLd data={{ '@context': 'https://schema.org', '@type': 'Article', headline: 'AI Marketing Agent for Products at Day Zero', dateModified: '2026-07-24', author: { '@type': 'Organization', name: 'Growth Lab' }, mainEntityOfPage: url }} />
      <SeoShell eyebrow="PRODUCT GUIDE / AI MARKETING AGENT" title="An AI marketing agent can own the zero-to-one growth loop." intro="Give Growth Lab a product idea, repository, prototype, or URL. It understands the product, develops and tests customer hypotheses, executes the first growth actions, and learns from results inside Codex or Claude Code.">
        <p>Early products rarely have a complete marketing brief. They may have no customers, campaign history, analytics, positioning, or confirmed ideal customer profile. Growth Lab does not require the founder to arrive with those answers. Its Skills guide the agent to inspect the product, form hypotheses, collect evidence, and execute the first measurable action.</p>

        <h2>What the agent does from day zero</h2>
        <div className="decision-grid">
          <div><strong>Understand the product</strong><span>Read code, routes, docs, onboarding, pricing, and existing product claims.</span></div>
          <div><strong>Form hypotheses</strong><span>Describe possible users, situations, urgent jobs, and signals that would challenge each guess.</span></div>
          <div><strong>Collect evidence</strong><span>Research live searches, communities, competitors, public content, and available product data.</span></div>
          <div><strong>Create a signal</strong><span>Ship a page, campaign, distribution action, or experiment that can produce observable feedback.</span></div>
        </div>

        <h2>Why the repository matters</h2>
        <p>Marketing work often starts from a manually written brief. A coding agent can inspect the product itself. It can see which features exist, how the site describes them, where activation happens, which events are already tracked, and what can be changed in the current codebase.</p>
        <p>This product-native context improves both research and execution. The same session that identifies a search opportunity can create a route, write the page, add metadata, test the rendering, connect analytics, deploy through the existing workflow, and inspect the result.</p>

        <h2>What to automate first</h2>
        <p>Choose work with a short, inspectable path from action to evidence.</p>
        <table>
          <thead><tr><th>Loop</th><th>Observation</th><th>Action</th><th>Review signal</th></tr></thead>
          <tbody>
            <tr><td>SEO page</td><td>User situations and search demand</td><td>Create and publish a useful page</td><td>Index status, queries, impressions, clicks, product actions</td></tr>
            <tr><td>Release distribution</td><td>Product change and relevant audiences</td><td>Create channel-specific release materials</td><td>Reach, visits, signups, activation</td></tr>
            <tr><td>Onboarding</td><td>Where early users stop</td><td>Change one onboarding decision</td><td>Completion and activation</td></tr>
            <tr><td>Content learning</td><td>Questions and high-performing patterns</td><td>Create and distribute one content package</td><td>Qualified engagement and product movement</td></tr>
          </tbody>
        </table>

        <h2>The agent builds the data path</h2>
        <p>The user provides the product and a desired outcome. The agent inspects existing instrumentation and can add events, connect an analytics provider, import available exports, or create a lightweight local collection path that fits the current stage.</p>
        <p>As real users arrive, first-party signals replace assumptions. The loop can revise its user model, channel choice, content, or product action from evidence.</p>

        <h2>Human collaboration remains useful</h2>
        <p>A person provides access, legal or brand judgment, and account-sensitive actions. The agent can prepare a complete publication package with final copy, assets, target channel, settings, links, and operating instructions. The person publishes through the platform’s normal interface, and the agent uses the resulting URL or screenshot for review.</p>

        <h2>How Growth Lab packages an agent</h2>
        <ul>
          <li><strong>Model:</strong> the observation-action-review loop.</li>
          <li><strong>Collectors:</strong> methods and Clients for obtaining evidence.</li>
          <li><strong>Executors:</strong> creation principles and tools for completing work.</li>
          <li><strong>Memory:</strong> dated operational evidence, outcomes, and the next recommendation.</li>
          <li><strong>Runtime:</strong> the Codex or Claude Code session controlling the work.</li>
        </ul>

        <p>All five live in or around the product workspace. Growth Lab is open source and free to use. The team can read the method, inspect outputs, change a Skill, and use the new version immediately. Starting requires only cloning the repository and opening it with Codex or Claude Code.</p>
      </SeoShell>
    </>
  );
}
