import type { Metadata } from 'next';
import { Bricolage_Grotesque, IBM_Plex_Mono, Inter } from 'next/font/google';
import { Analytics } from '@/components/analytics';
import { SiteFooter } from '@/components/site-footer';
import { SiteHeader } from '@/components/site-header';
import { getSiteUrl } from '@/lib/site';
import './globals.css';

const display = Bricolage_Grotesque({ subsets: ['latin'], variable: '--font-display' });
const body = Inter({ subsets: ['latin'], variable: '--font-body' });
const mono = IBM_Plex_Mono({ subsets: ['latin'], weight: ['400', '500', '600'], variable: '--font-mono' });

export const metadata: Metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: { default: 'Growth Lab — Your coding agent, from code to market', template: '%s · Growth Lab' },
  description: 'An open-source, end-to-end growth tool executed by Codex and Claude Code inside your product workspace.',
  alternates: { canonical: '/' },
  openGraph: {
    type: 'website',
    title: 'Growth Lab — Your coding agent, from code to market',
    description: 'Research demand, create growth assets, execute, measure, and learn inside your coding workspace.',
    url: '/',
    siteName: 'Growth Lab',
  },
  twitter: { card: 'summary_large_image' },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body>
        <SiteHeader />
        {children}
        <SiteFooter />
        <Analytics />
      </body>
    </html>
  );
}
