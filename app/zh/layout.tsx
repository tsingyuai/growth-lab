import type { Metadata } from 'next';
import { languageAlternates } from '@/lib/site';

export const metadata: Metadata = {
  title: { absolute: 'Growth Lab — 让 Coding Agent 从代码走向市场' },
  description: '由 Codex 和 Claude Code 在产品工作区中执行的开源端到端增长工具。',
  alternates: { canonical: '/zh', languages: languageAlternates('/') },
  openGraph: {
    type: 'website',
    title: 'Growth Lab — 让 Coding Agent 从代码走向市场',
    description: '在 Coding Workspace 中完成需求调研、内容创作、执行、度量与复盘。',
    url: '/zh',
    siteName: 'Growth Lab',
    locale: 'zh_CN',
  },
};

export default function ChineseLayout({ children }: { children: React.ReactNode }) {
  return children;
}
