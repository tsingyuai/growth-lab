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
      <section className="positioning-grid" aria-label={isZh ? 'Growth Lab 产品特性' : 'Growth Lab product facts'}>
        <div>
          <span>01 / {isZh ? '端到端' : 'END TO END'}</span>
          <strong>{isZh ? '从产品到第一条增长结果' : 'From product to the first growth result'}</strong>
          <p>{isZh ? 'Agent 自己理解产品、形成客户假设、采集市场证据并完成执行，帮助产品从 0 走到 1。' : 'The agent reads the product, forms customer hypotheses, collects market evidence, and executes the work from zero to one.'}</p>
        </div>
        <div>
          <span>02 / {isZh ? '开源免费' : 'OPEN & FREE'}</span>
          <strong>{isZh ? '方法、工具和记忆都在你的工作区' : 'Methods, tools, and memory stay in your workspace'}</strong>
          <p>{isZh ? '完整代码与 Skills 开源可读，可以直接使用、检查、修改并组合进自己的产品。' : 'The code and Skills are open source, inspectable, editable, and free to run with your product.'}</p>
        </div>
        <div>
          <span>03 / {isZh ? '一句话交互' : 'ONE CONVERSATION'}</span>
          <strong>{isZh ? '继续使用 Codex 或 Claude Code' : 'Use Codex or Claude Code you already know'}</strong>
          <p>{isZh ? 'Clone 仓库、打开工作区、描述目标即可开始，无需学习新软件、注册新的 SaaS 或手动填写大量配置。' : 'Clone the repo, open the workspace, and describe the goal—no new software UI, SaaS signup, or configuration project.'}</p>
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
