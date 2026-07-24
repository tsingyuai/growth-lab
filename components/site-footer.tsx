import Link from 'next/link';
import { githubUrl } from '@/lib/site';

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div>
        <span className="utility-label">OPEN SOURCE · AGENT NATIVE</span>
        <p>Growth from code to market, executed inside your coding workspace.</p>
      </div>
      <div className="footer-links">
        <Link href="/ai-marketing-tools">AI marketing tools</Link>
        <Link href="/agentic-marketing">Agentic marketing</Link>
        <Link href="/ai-marketing-agent">AI marketing agent</Link>
        <Link href="/ai-seo-agent">AI SEO agent</Link>
        <a href={githubUrl}>GitHub</a>
      </div>
    </footer>
  );
}
