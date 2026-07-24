import type { MetadataRoute } from 'next';
import { getSiteUrl, seoPages } from '@/lib/site';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = getSiteUrl();
  const lastModified = new Date('2026-07-24');
  return [
    { url: baseUrl, lastModified, changeFrequency: 'weekly', priority: 1 },
    ...seoPages.map((path) => ({
      url: `${baseUrl}${path}`,
      lastModified,
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    })),
  ];
}
