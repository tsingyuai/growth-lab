'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { githubUrl } from '@/lib/site';

export function SiteHeader() {
  const pathname = usePathname();
  const isZh = pathname === '/zh' || pathname.startsWith('/zh/');
  const localize = (path: string) => isZh ? `/zh${path === '/' ? '' : path}` : path;
  const alternatePath = isZh ? (pathname.replace(/^\/zh/, '') || '/') : `/zh${pathname === '/' ? '' : pathname}`;
  return (
    <header className="site-header">
      <Link className="wordmark" href={localize('/')} aria-label="Growth Lab home">
        <span className="wordmark-mark" aria-hidden="true">GL</span>
        <span>Growth Lab</span>
      </Link>
      <nav aria-label={isZh ? '主导航' : 'Primary navigation'}>
        <Link href={`${localize('/')}#capability`}>{isZh ? '现有能力' : 'Capability'}</Link>
        <Link href={localize('/agentic-marketing')}>{isZh ? '指南' : 'Guide'}</Link>
        <Link className="language-switch" href={alternatePath} hrefLang={isZh ? 'en' : 'zh-CN'}>{isZh ? 'EN' : '中文'}</Link>
        <a href={githubUrl} target="_blank" rel="noreferrer">GitHub ↗</a>
      </nav>
    </header>
  );
}
