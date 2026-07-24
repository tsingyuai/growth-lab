import Link from 'next/link';
import type { ReactNode } from 'react';
import { githubUrl } from '@/lib/site';

type SeoShellProps = {
  eyebrow: string;
  title: string;
  intro: string;
  children: ReactNode;
  updated?: string;
};

export function SeoShell({ eyebrow, title, intro, children, updated = 'July 24, 2026' }: SeoShellProps) {
  return (
    <main className="article-page">
      <section className="article-hero">
        <div className="article-kicker">{eyebrow}</div>
        <h1>{title}</h1>
        <p className="article-intro">{intro}</p>
        <div className="article-meta">
          <span>Growth Lab research note</span>
          <span>Updated {updated}</span>
        </div>
      </section>
      <article className="article-body">{children}</article>
      <section className="article-cta">
        <span className="utility-label">RUN IT IN YOUR REPO</span>
        <h2>Give your coding agent a growth loop.</h2>
        <p>Clone Growth Lab, open the workspace in Codex or Claude Code, and start with the product you already have.</p>
        <div className="button-row">
          <a className="button button-primary" href={githubUrl}>Open on GitHub ↗</a>
          <Link className="button button-quiet" href="/ai-seo-agent">See the SEO loop</Link>
        </div>
      </section>
    </main>
  );
}
