import Link from 'next/link';
import type { ReactNode } from 'react';
import { githubUrl } from '@/lib/site';

type SeoShellProps = {
  eyebrow: string;
  title: string;
  intro: string;
  children: ReactNode;
  updated?: string;
  locale?: 'en' | 'zh';
};

export function SeoShell({ eyebrow, title, intro, children, updated = 'July 24, 2026', locale = 'en' }: SeoShellProps) {
  const isZh = locale === 'zh';
  return (
    <main className="article-page">
      <section className="article-hero">
        <div className="article-kicker">{eyebrow}</div>
        <h1>{title}</h1>
        <p className="article-intro">{intro}</p>
        <div className="article-meta">
          <span>{isZh ? 'Growth Lab 研究笔记' : 'Growth Lab research note'}</span>
          <span>{isZh ? `更新于 ${updated}` : `Updated ${updated}`}</span>
        </div>
      </section>
      <article className="article-body">{children}</article>
      <section className="article-cta">
        <span className="utility-label">{isZh ? '在你的仓库中运行' : 'RUN IT IN YOUR REPO'}</span>
        <h2>{isZh ? '给你的 Coding Agent 一个增长闭环。' : 'Give your coding agent a growth loop.'}</h2>
        <p>{isZh ? 'Clone Growth Lab，在 Codex 或 Claude Code 中打开工作区，从你已有的产品开始。' : 'Clone Growth Lab, open the workspace in Codex or Claude Code, and start with the product you already have.'}</p>
        <div className="button-row">
          <a className="button button-primary" href={githubUrl}>{isZh ? '在 GitHub 打开 ↗' : 'Open on GitHub ↗'}</a>
          <Link className="button button-quiet" href={isZh ? '/zh/ai-seo-agent' : '/ai-seo-agent'}>{isZh ? '查看 SEO 闭环' : 'See the SEO loop'}</Link>
        </div>
      </section>
    </main>
  );
}
