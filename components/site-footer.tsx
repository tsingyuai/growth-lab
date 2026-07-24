'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { githubUrl } from '@/lib/site';

export function SiteFooter() {
  const pathname = usePathname();
  const isZh = pathname === '/zh' || pathname.startsWith('/zh/');
  const localize = (path: string) => isZh ? `/zh${path}` : path;
  return (
    <footer className="site-footer">
      <div>
        <span className="utility-label">{isZh ? '开源 · AGENT 原生' : 'OPEN SOURCE · AGENT NATIVE'}</span>
        <p>{isZh ? '从代码走向市场，由 Coding Agent 在你的工作区中完成。' : 'Growth from code to market, executed inside your coding workspace.'}</p>
      </div>
      <div className="footer-links">
        <Link href={localize('/ai-marketing-tools')}>{isZh ? 'AI 营销工具' : 'AI marketing tools'}</Link>
        <Link href={localize('/agentic-marketing')}>{isZh ? 'Agentic Marketing' : 'Agentic marketing'}</Link>
        <Link href={localize('/ai-marketing-agent')}>{isZh ? 'AI 营销 Agent' : 'AI marketing agent'}</Link>
        <Link href={localize('/ai-seo-agent')}>{isZh ? 'AI SEO Agent' : 'AI SEO agent'}</Link>
        <a href={githubUrl}>GitHub</a>
      </div>
    </footer>
  );
}
