import type { MetadataRoute } from 'next';
import { getSiteUrl, languageAlternates, seoPages } from '@/lib/site';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = getSiteUrl();
  const lastModified = new Date('2026-07-24');
  const absoluteAlternates = (path: string) => Object.fromEntries(
    Object.entries(languageAlternates(path)).map(([language, value]) => [language, `${baseUrl}${value === '/' ? '' : value}`])
  );
  return [
    { url: baseUrl, lastModified, changeFrequency: 'weekly', priority: 1, alternates: { languages: absoluteAlternates('/') } },
    { url: `${baseUrl}/zh`, lastModified, changeFrequency: 'weekly', priority: 1, alternates: { languages: absoluteAlternates('/') } },
    ...seoPages.flatMap((path) => [{
      url: `${baseUrl}${path}`,
      lastModified,
      changeFrequency: 'weekly' as const,
      priority: 0.8,
      alternates: { languages: absoluteAlternates(path) },
    }, {
      url: `${baseUrl}/zh${path}`,
      lastModified,
      changeFrequency: 'weekly' as const,
      priority: 0.8,
      alternates: { languages: absoluteAlternates(path) },
    }]),
  ];
}
