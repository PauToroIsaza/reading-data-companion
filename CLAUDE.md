# Claude Code Preferences

## Git Workflow

**NEVER execute any git commands.** This includes:
- `git add`, `git commit`, `git push`, `git pull`
- `git checkout`, `git branch`, `git merge`
- Any other git operations

Instead:
- Prompt the user when it's a good time to commit (after completing a feature, fixing a bug, reaching a milestone)
- Suggest descriptive branch names when starting new features
- Suggest commit messages that follow conventional commits format (e.g., `feat:`, `fix:`, `docs:`, `refactor:`)

## Testing

- Write tests alongside each new feature
- Always remind the user to run tests before committing
- Test files should be co-located or in a `__tests__` directory as appropriate for the framework

## Dependencies

**Always ask before adding a new package.** When proposing a dependency:
1. Explain why it's needed
2. Describe what alternatives exist
3. Note any tradeoffs (bundle size, maintenance status, learning curve)
4. Wait for approval before adding to package.json

## Documentation

Do not write documentation (README files, JSDoc comments, etc.) unless explicitly requested.

## Code Style

No specific preferences configured yet. Follow existing patterns in the codebase.

## Visualization Libraries

Open to exploring alternatives to the suggested tooling in `architecture_brief.md`. When proposing a visualization approach, discuss options rather than assuming one.

## Data Pipeline

Python (in `packages/data-pipeline/`) is the primary tool for data processing and analysis. The web layer consumes the processed JSON output.

## Project Context

This is an Astro-based monorepo for interactive data journalism. See `architecture_brief.md` for full architecture details.

- Package manager: **pnpm**
- Structure: monorepo with `apps/web/`, `packages/ui-patterns/`, `packages/data-pipeline/`
- Content: MDX essays with embedded visualization components
