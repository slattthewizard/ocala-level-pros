import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import fs from 'node:fs';
import path from 'node:path';

/**
 * lastmod per URL.
 * Blog posts use their frontmatter publishedDate/updatedDate; everything
 * else falls back to the source file's mtime so edits surface to crawlers.
 */
const blogDates = new Map();
const blogDir = path.resolve('./src/content/blog');
if (fs.existsSync(blogDir)) {
  for (const file of fs.readdirSync(blogDir)) {
    if (!file.endsWith('.md')) continue;
    const raw = fs.readFileSync(path.join(blogDir, file), 'utf-8');
    const updated = raw.match(/^updatedDate:\s*"(.*?)"/m);
    const published = raw.match(/^publishedDate:\s*"(.*?)"/m);
    const d = (updated || published)?.[1];
    if (d) blogDates.set(`/blog/${file.replace(/\.md$/, '')}/`, d);
  }
}

const pageMtime = (pathname) => {
  const rel = pathname.replace(/^\/|\/$/g, '');
  const candidates = [
    `./src/pages/${rel}/index.astro`,
    `./src/pages/${rel}.astro`,
    './src/pages/index.astro',
  ];
  for (const c of candidates) {
    const abs = path.resolve(c);
    if (fs.existsSync(abs)) return fs.statSync(abs).mtime;
  }
  return new Date();
};

export default defineConfig({
  site: 'https://ocalalevelpros.com',
  integrations: [
    sitemap({
      serialize(item) {
        const { pathname } = new URL(item.url);
        const known = blogDates.get(pathname);
        item.lastmod = known
          ? new Date(`${known}T12:00:00Z`).toISOString()
          : pageMtime(pathname).toISOString();
        return item;
      },
    }),
  ],
});
