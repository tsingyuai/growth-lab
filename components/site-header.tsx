import Link from 'next/link';
import { githubUrl } from '@/lib/site';

export function SiteHeader() {
  return (
    <header className="site-header">
      <Link className="wordmark" href="/" aria-label="Growth Lab home">
        <span className="wordmark-mark" aria-hidden="true">GL</span>
        <span>Growth Lab</span>
      </Link>
      <nav aria-label="Primary navigation">
        <Link href="/#capability">Capability</Link>
        <Link href="/agentic-marketing">Guide</Link>
        <a href={githubUrl} target="_blank" rel="noreferrer">GitHub ↗</a>
      </nav>
    </header>
  );
}
