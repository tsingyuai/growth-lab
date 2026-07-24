import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl, languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: 'Agentic Marketing: A Practical Operating Model',
  description: 'Agentic marketing connects observation, tool use, execution, measurement, and memory. Learn the operating model and build a first useful loop.',
  alternates: { canonical: '/agentic-marketing', languages: languageAlternates('/agentic-marketing') },
  openGraph: { title: 'Agentic Marketing: A Practical Operating Model', description: 'A concrete guide to building marketing loops that observe, act, review, and remember.', url: '/agentic-marketing' },
};

export default function AgenticMarketingPage() {
  const url = `${getSiteUrl()}/agentic-marketing`;
  return (
    <>
      <JsonLd data={{ '@context': 'https://schema.org', '@type': 'Article', headline: 'Agentic Marketing: A Practical Operating Model', dateModified: '2026-07-24', author: { '@type': 'Organization', name: 'Growth Lab' }, mainEntityOfPage: url }} />
      <SeoShell eyebrow="FIELD GUIDE / AGENTIC MARKETING" title="Agentic marketing is a loop that can act on what it learns." intro="A useful marketing agent observes evidence, chooses a bounded action, uses tools to complete it, reviews the outcome, and carries the result into the next decision.">
        <p>Agentic marketing turns a marketing method into executable instructions for an AI agent. The agent receives a goal and product context, selects relevant tools, completes work, checks the result, and preserves evidence for the next run.</p>
        <p>This definition is close to the practical distinction described in <a href="https://ahrefs.com/blog/agentic-marketing/">Ahrefs’ guide to agentic marketing</a>: the agent selects steps and tools and continues until the job is completed. Growth Lab adds a persistent review loop around that execution.</p>

        <h2>The five parts of a working marketing agent</h2>
        <table>
          <thead><tr><th>Part</th><th>Question</th><th>Example</th></tr></thead>
          <tbody>
            <tr><td>Observation</td><td>What changed in the market or product?</td><td>New search queries reached a page.</td></tr>
            <tr><td>Decision</td><td>Which single action is supported by evidence?</td><td>Rewrite the title around the arriving intent.</td></tr>
            <tr><td>Execution</td><td>Which tools complete the action?</td><td>Edit Next.js metadata, test, deploy, submit IndexNow.</td></tr>
            <tr><td>Review</td><td>What outcome followed?</td><td>Compare impressions, position, CTR, and activation.</td></tr>
            <tr><td>Memory</td><td>What should the next run know?</td><td>Date, evidence, action, result, and next recommendation.</td></tr>
          </tbody>
        </table>

        <h2>Start with one narrow loop</h2>
        <p>A narrow loop has a recognizable observation, an action surface the agent can reach, and an outcome that arrives within a useful time window. SEO pages, release distribution, onboarding analysis, and content repurposing can each form a separate loop.</p>

        <pre><code>{`Read Memory
→ observe one signal
→ choose one action
→ invoke the required tools
→ inspect the result
→ wait for the outcome
→ review and write Memory`}</code></pre>

        <p>Each loop benefits from specialized methods. A demand-research Skill should know how to expand keyword families and validate intent. A page-creation Skill should know how to create information gain. A review Skill should know how to remove generic content. Specialization keeps the loop concrete.</p>

        <h2>What the agent needs access to</h2>
        <h3>The product</h3>
        <p>Repository access lets a coding agent see features, routes, onboarding, content, analytics hooks, and constraints in their real form. A live URL or product brief can support an earlier product.</p>

        <h3>The outside world</h3>
        <p>Search and browser access support market observation. Official APIs, exports, and authorized Clients provide structured data or external actions. Credentials stay in environment variables.</p>

        <h3>A place to remember outcomes</h3>
        <p>Memory holds dated operational evidence and next actions. The agent reads it before a new observation. The loop method remains in its Skill, where the team can inspect and improve it directly.</p>

        <h2>A 0→1 agentic marketing loop</h2>
        <ol>
          <li>Open the product repository or describe the product idea.</li>
          <li>Ask the agent to form user and usage-scenario hypotheses.</li>
          <li>Collect public demand evidence around those scenarios.</li>
          <li>Choose one action that can create a measurable signal.</li>
          <li>Add or connect the smallest analytics path required to see the outcome.</li>
          <li>Execute, review, preserve the result, and choose what follows.</li>
        </ol>

        <h2>Control stays in the session</h2>
        <p>The Codex or Claude Code session is the control plane. It reads Skills, uses native browser and coding tools, invokes Clients for external APIs, edits the workspace, and collaborates with the user when access or judgment is required.</p>
        <p>This model keeps the method readable. A team can improve the loop while using it, replace a Client, or inspect the evidence behind a decision.</p>
      </SeoShell>
    </>
  );
}
