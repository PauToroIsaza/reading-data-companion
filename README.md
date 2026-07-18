# Reading Data Companion

A multi-book website featuring interactive data visualizations that accompany nonfiction books. Each book gets its own section with essays (one per chapter) and explorable charts, maps, and tools that let readers interrogate the claims in the text.

## Tech Stack

- **Framework:** Astro with MDX content collections
- **Visualizations:** Astro islands (React components hydrated client-side)
- **Data processing:** Python
- **Package manager:** pnpm

## Project Structure

```
apps/web/                  # Astro site
packages/ui-patterns/      # Shared visualization components
packages/data-pipeline/    # Python data processing scripts
data/raw/<book>/           # Source datasets
data/processed/<book>/     # Cleaned data consumed by the site
content/books/<book>/      # MDX essays
```

See `architecture_brief.md` for detailed architecture decisions.
