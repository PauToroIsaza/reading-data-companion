import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const books = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/books' }),
  schema: z.object({
    title: z.string(),
    chapter: z.number(),
    book: z.string(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { books };
