import type { Metadata } from 'next';
import { JsonLd } from '@/components/json-ld';
import { SeoShell } from '@/components/seo-shell';
import { getSiteUrl, languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: 'AI SEO Agent: From User Scenario to Measured Page',
  description: 'See how an AI SEO agent researches real searches, creates an information-rich page, submits it to IndexNow, and reviews Bing outcomes.',
  alternates: { canonical: '/ai-seo-agent', languages: languageAlternates('/ai-seo-agent') },
  openGraph: { title: 'AI SEO Agent: From User Scenario to Measured Page', description: 'A complete SEO page loop executed inside the product workspace.', url: '/ai-seo-agent' },
};

export default function AiSeoAgentPage() {
  const url = `${getSiteUrl()}/ai-seo-agent`;
  return (
    <>
      <JsonLd data={{ '@context': 'https://schema.org', '@type': 'HowTo', name: 'Run an AI SEO page growth loop', description: 'Research, create, publish, measure, and iterate an SEO page with a coding agent.', dateModified: '2026-07-24', mainEntityOfPage: url, step: ['Understand product scenarios', 'Research real searches', 'Study winning pages', 'Create and review the page', 'Deploy and submit IndexNow', 'Review Bing and product outcomes'].map((name, index) => ({ '@type': 'HowToStep', position: index + 1, name })) }} />
      <SeoShell eyebrow="CAPABILITY / AI SEO AGENT" title="From a user scenario to a measured SEO page." intro="The Growth Lab SEO agent researches what users actually search, creates a page with information gain, ships it in the product, and uses Bing and product outcomes to choose the next action.">
        <p>An SEO page is valuable when it resolves a real user situation and creates a natural path into the product. The agent begins with the product, discovers possible situations of need, validates the language users search, and creates the page inside the actual codebase.</p>

        <h2>The complete SEO page loop</h2>
        <ol>
          <li><strong>Read Memory.</strong> Recover previous observations, actions, outcomes, and recommendations for the product or query family.</li>
          <li><strong>Observe demand.</strong> Expand keyword families, validate Bing demand when available, and inspect live SERPs with the Runtime browser.</li>
          <li><strong>Choose one page.</strong> Require observable demand, stable intent, product fit, a useful gap, and a credible product outcome.</li>
          <li><strong>Create.</strong> Match the winning page shape, add original evidence and useful artifacts, implement metadata and structured data, and generate relevant images.</li>
          <li><strong>Review adversarially.</strong> Apply deletion, reversal, title-swap, brand-removal, evidence, image-text, and conversion tests.</li>
          <li><strong>Ship.</strong> Run product checks, inspect the rendered page, deploy, and submit the live URL through IndexNow.</li>
          <li><strong>Review outcomes.</strong> Compare crawl status, queries, impressions, positions, clicks, CTR, and relevant product actions.</li>
          <li><strong>Write Memory.</strong> Preserve the evidence, conclusion, observed result, and next recommended action.</li>
        </ol>

        <h2>How the agent finds a page opportunity</h2>
        <p>The agent starts from situations in which a user may need the product. It expands each situation across concepts, actions, tools, resources, competitors, and questions. It uses live autocomplete, related searches, SERP pages, communities, reviews, and support language to discover expressions people already use.</p>
        <p>When Bing Webmaster API access is available, the agent compares weekly exact impressions among phrases with similar specificity. It treats empty data as unavailable evidence and checks intent directly in the live results.</p>

        <h2>What makes the page worth indexing</h2>
        <p>The agent studies the first relevant results as three layers:</p>
        <ul>
          <li><strong>Search layer:</strong> title, description, headings, canonical, structured data, internal links, and freshness.</li>
          <li><strong>User layer:</strong> visible sequence, task completion, trust, useful images, and conversion path.</li>
          <li><strong>Quality layer:</strong> unique information, concrete data, sources, authorship, originality, and genuine effort.</li>
        </ul>
        <p>The new page then fills a gap with procedures, examples, quality criteria, real product evidence, original analysis, copyable artifacts, primary sources, or useful constraints.</p>

        <h2>The page is tested as a user would see it</h2>
        <p>The Runtime opens the local and deployed page with its native browser. It checks visible content, mobile behavior, metadata, canonical, JSON-LD, images, internal links, console errors, failed requests, and public accessibility.</p>
        <p>The adversarial review removes blocks that add no user value, generic advice, claims without evidence, repeated conversion, interchangeable template content, and images that fail to show the task described beside them.</p>

        <h2>Observed result from a real run</h2>
        <table>
          <thead><tr><th>Signal</th><th>Observed change</th><th>What enters the next review</th></tr></thead>
          <tbody>
            <tr><td>Indexing</td><td>New pages indexed in 1–2 days</td><td>Discovery path worked for this run</td></tr>
            <tr><td>Impressions</td><td>+1000% on a 7-day average</td><td>The pages reached substantially more searches</td></tr>
            <tr><td>Clicks</td><td>+1000% on a 7-day average</td><td>The added reach produced more visits</td></tr>
            <tr><td>Overall CTR</td><td>−50% on a 7-day average</td><td>Query mix and snippet fit require a separate diagnosis</td></tr>
          </tbody>
        </table>
        <p>These figures describe one observed run. The next loop reads the arriving queries and page-level outcomes before choosing whether to improve the snippet, strengthen intent fit, add evidence, adjust conversion, or allow more time for data.</p>

        <h2>Run the capability in your product</h2>
        <pre><code>{`git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab

# Open the workspace in Codex or Claude Code
# Invoke run-seo-page-loop with your product path or URL`}</code></pre>
        <p>The Model coordinates dedicated Skills for demand research, page creation, image generation, adversarial review, IndexNow submission, and Bing performance review. Browser inspection and local page testing use the Runtime’s native abilities.</p>
      </SeoShell>
    </>
  );
}
