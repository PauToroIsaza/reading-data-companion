import { vizManifestSchema, type VizManifest, type VizEntry } from './viz-schema';

/**
 * All viz manifests, keyed by their path relative to content/books/.
 * Vite resolves these at build time.
 */
const manifests = import.meta.glob<{ default: unknown }>(
  '/src/content/books/**/*.viz.json',
  { eager: true }
);

/**
 * Load and validate a chapter's viz manifest.
 *
 * @param book - Book slug (e.g., "the-grid")
 * @param chapter - Chapter number
 * @returns Validated viz manifest, or empty array if no manifest exists
 * @throws If manifest exists but fails validation
 */
export function loadVizManifest(book: string, chapter: number): VizManifest {
  const path = `/src/content/books/${book}/chapter-${chapter}.viz.json`;
  const module = manifests[path];

  if (!module) {
    return [];
  }

  const result = vizManifestSchema.safeParse(module.default);

  if (!result.success) {
    throw new Error(
      `Invalid viz manifest at ${path}:\n${result.error.issues.map((i) => `  - ${i.path.join('.')}: ${i.message}`).join('\n')}`
    );
  }

  return result.data;
}

/**
 * Get a specific visualization entry by ID from a chapter's manifest.
 *
 * @param book - Book slug
 * @param chapter - Chapter number
 * @param vizId - The visualization's id field
 * @returns The viz entry, or undefined if not found
 */
export function getVizEntry(book: string, chapter: number, vizId: string): VizEntry | undefined {
  const manifest = loadVizManifest(book, chapter);
  return manifest.find((entry) => entry.id === vizId);
}
