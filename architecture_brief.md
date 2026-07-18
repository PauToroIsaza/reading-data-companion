# Reading Data Companion — Architecture Brief

## Goal

Build a multi-book website where each nonfiction book gets its own section
("sub-site") of essays, one per chapter/section, each essay accompanied by
interactive data visualizations that let the reader interrogate the claims
in the text — not static charts, but explorable ones (e.g. entering a zip
code to see personal outage history for a book about the power grid).

This is closer to data-journalism/interactive-explainer work (NYT
interactive graphics, Washington Post data pieces, Pudding.cool) than a
blog or a book-review site. The site will host a genuinely wide range of
nonfiction subjects, so the underlying data and interaction patterns will
vary a lot from book to book.

Framework direction: **Astro**, using content collections
(`content/books/<book>/chapter-N.mdx`) with MDX so essays can embed live
visualization components directly in the prose. Visualizations render as
Astro islands (only the interactive components hydrate client-side).
Subdirectory routing (`/books/the-grid/`) rather than true subdomains,
unless a specific need for domain separation emerges later.

---

## The 8 Recurring Interaction Patterns

Across nonfiction subjects, reader-facing interactivity tends to fall into
one of these patterns. Design around the *pattern*, not the chart type or
subject matter:

1. **Lookup** — reader inputs something personal (zip code, income, age,
   company name) and sees themselves against the dataset.
2. **Scrollytelling** — a visualization builds/transforms as the reader
   scrolls through the argument (annotations appear, a chart re-sorts, a
   map zooms).
3. **Explorable tables** — a searchable, sortable, filterable dataset
   (e.g. "browse all 500 companies in this analysis").
4. **Comparison/ranking** — bar charts, dot plots, slope charts; mostly
   hover-for-detail and toggle-a-category interactivity.
5. **Flow/relationship diagrams** — Sankey (money/energy flow), network
   graphs (org structures, supply chains, funding relationships).
6. **Time series with brushing/zoom** — long historical trends the reader
   can drag/zoom into.
7. **Geospatial** — maps, choropleths, point-density visualizations.
8. **Simulators/calculators** — reader adjusts an input (a slider, a
   parameter) and a projection or output updates live.

Suggested tooling by pattern (not prescriptive — a starting point):

| Pattern | Tool |
|---|---|
| Lookup | React/JS state + precomputed static JSON, any chart lib for the result |
| Scrollytelling | `scrollama` / `react-scrollama` for step-detection |
| Explorable tables | `TanStack Table` (headless) |
| Comparison/ranking | Observable Plot |
| Flow/network | D3 (Sankey plugin, force-directed graph) |
| Time series w/ brushing | Observable Plot or D3 (native brush behavior) |
| Geospatial | MapLibre GL JS (deck.gl only if rendering very large point clouds) |
| Simulator/calculator | React state + a formula/model function, chart lib for output |

---

## Sequencing: Rule of Three, Don't Pre-Build the Toolkit

Don't build all 8 generic pattern components before there's real content —
the interfaces will be guessed wrong until real data forces their shape.

1. **Book #1**: build hand-rolled, slightly-too-specific components for
   whatever patterns that book actually needs.
2. **Book #2**: reuse roughly half directly; the rest will need
   close-but-different versions — this is expected, not a failure of
   planning.
3. **Extract the shared abstraction now** — after two concrete cases, the
   real variance points are known rather than guessed (e.g. a zip lookup
   for power outages vs. a zip lookup for school ratings look identical
   until edge cases like zip codes spanning multiple states show up).

This is the standard "rule of three," applied deliberately because
interactive data components tend to have deeper hidden variance than
typical UI components.

### Suggested repo structure

```
apps/
  web/                    ← Astro site, all books
packages/
  ui-patterns/            ← shared pattern-level components, grows over time
    DataLookup/
    ScrollyFrame/
    ExplorableTable/
    Simulator/
  data-pipeline/          ← data analysis scripts (Python), one subfolder per book
    the-grid/
    book-2/
data/
  raw/<book>/             ← source datasets, untouched
  processed/<book>/       ← cleaned/aggregated output, consumed by the site
content/
  books/<book>/chapter-N.mdx
```

Monorepo (npm/pnpm workspaces) — `ui-patterns` versioned alongside the site,
no publishing overhead needed at this scale, just clean import boundaries
(`import { DataLookup } from '@site/ui-patterns'`).

---

## Data Contract (the part worth designing carefully now)

Since it isn't known upfront which patterns future books will need, the
durable investment is a **consistent contract for how a chapter declares
its visualizations** — decoupled from which pattern eventually renders
them.

Per-chapter manifest, e.g.:

```json
// content/books/the-grid/chapter-1.viz.json
[
  { "id": "outage-lookup", "pattern": "lookup", "dataset": "processed/the-grid/outages-by-zip.json" },
  { "id": "national-trend", "pattern": "timeseries", "dataset": "processed/the-grid/outages-1990-2024.json" }
]
```

The MDX essay references the viz by id (`<Viz id="outage-lookup" />`), and
a small resolver maps `pattern` → the matching component from
`ui-patterns`.

Benefits:
- Data pipeline work (cleaning, aggregating, writing to `processed/`) is
  fully decoupled from which UI pattern eventually renders it.
- New pattern types can be added later without touching old chapters.
- A single manifest per book shows every interactive piece in that book
  without opening each MDX file.

### Suggested tooling for the contract

- **TypeScript + Zod** — runtime-validate that `processed/<book>/*.json`
  actually matches what a pattern component expects, so pipeline drift
  fails loudly instead of silently breaking a chart.
- **Storybook**, scoped to the `ui-patterns` package only — once there are
  4–5 pattern components each reused across multiple books with different
  data, an isolated playground against fixture data pays for its setup
  cost.

### Lookup-pattern data note

For patterns like zip-code lookups, prefer precomputed static JSON
(sharded, e.g. by state, to avoid tens of thousands of tiny files) over a
live backend. Only add a real backend/database (e.g. Postgres + PostGIS)
when a chapter needs genuine geospatial querying (e.g. "outages within 50
miles of any point") that a static key lookup can't serve.