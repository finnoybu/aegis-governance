import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

/**
 * Resolve the site version from the committed VERSION file.
 *
 * VERSION is a JSON file in this site directory, written by the
 * nightly release rollup every time a 3-part release tag is cut.
 * The Header component in @aegis-initiative/design-system reads
 * `import.meta.env.AEGIS_VERSION`, which is populated here by
 * mutating `process.env` before Astro/Vite loads.
 *
 * Note: this inline helper will be migrated to
 * `@aegis-initiative/design-system/build`'s `readSiteVersion()`
 * once design-system v0.4.0 is published.
 */
function resolveVersion() {
  try {
    const here = dirname(fileURLToPath(import.meta.url));
    const raw = readFileSync(resolve(here, 'VERSION'), 'utf8');
    const parsed = JSON.parse(raw);
    return parsed.tag || 'dev';
  } catch {
    return 'dev';
  }
}

process.env.AEGIS_VERSION = resolveVersion();

export default defineConfig({
  site: 'https://aegis-governance.com',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      theme: 'github-dark-default',
    },
  },
});
