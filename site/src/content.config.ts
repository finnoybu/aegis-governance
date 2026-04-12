import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const docs = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/docs' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    sidebar: z.object({
      hidden: z.boolean().optional(),
      order: z.number().optional(),
    }).optional(),
  }),
});

export const collections = { docs };
