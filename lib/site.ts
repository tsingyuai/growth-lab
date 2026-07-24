export const githubUrl = 'https://github.com/tsingyuai/growth-lab';

export function getSiteUrl() {
  const configured = process.env.NEXT_PUBLIC_SITE_URL || process.env.SITE_URL;
  if (configured) return configured.replace(/\/$/, '');

  const vercelHost =
    process.env.VERCEL_PROJECT_PRODUCTION_URL || process.env.VERCEL_URL;
  if (vercelHost) return `https://${vercelHost}`;

  return 'http://localhost:3000';
}

export const seoPages = [
  '/ai-marketing-tools',
  '/agentic-marketing',
  '/ai-marketing-agent',
  '/ai-seo-agent',
] as const;
