import { defineCollection } from 'astro:content'
import { glob } from 'astro/loaders'
import { z } from 'astro/zod'

const courses = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/courses' }),
  schema: z.object({
    title: z.string(),
    slug: z.string().regex(/^[a-z0-9-]+$/),
    order: z.number().int().positive(),
    phase: z.string(),
    description: z.string(),
    duration: z.string(),
    level: z.string(),
    tags: z.array(z.string()),
    published: z.boolean().default(true)
  })
})

export const collections = { courses }
