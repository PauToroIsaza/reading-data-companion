import { z } from 'zod';

/**
 * The 8 recurring interaction patterns from the architecture brief.
 */
export const vizPatterns = [
  'lookup',        // Reader inputs something personal, sees themselves in the data
  'scrollytelling', // Visualization transforms as reader scrolls
  'table',         // Searchable, sortable, filterable dataset
  'comparison',    // Bar charts, dot plots, rankings with hover/toggle
  'flow',          // Sankey diagrams, network graphs, relationships
  'timeseries',    // Historical trends with brush/zoom
  'geo',           // Maps, choropleths, point-density
  'simulator',     // Adjust inputs, see projections update
] as const;

export type VizPattern = (typeof vizPatterns)[number];

/**
 * Schema for a single visualization entry in a chapter's viz manifest.
 */
export const vizEntrySchema = z.object({
  id: z.string().describe('Unique identifier referenced by <Viz id="..." /> in MDX'),
  pattern: z.enum(vizPatterns).describe('Which interaction pattern this visualization uses'),
  dataset: z.string().describe('Path to processed data JSON, relative to data/'),
  interactive: z.boolean().default(true).describe('Whether the viz needs client-side JS'),
  description: z.string().optional().describe('Accessibility description for screen readers'),
  sources: z.array(z.string()).optional().describe('Data attribution / citations'),
  config: z.record(z.unknown()).optional().describe('Pattern-specific configuration'),
});

export type VizEntry = z.infer<typeof vizEntrySchema>;

/**
 * Schema for a chapter's complete viz manifest (array of entries).
 */
export const vizManifestSchema = z.array(vizEntrySchema);

export type VizManifest = z.infer<typeof vizManifestSchema>;
