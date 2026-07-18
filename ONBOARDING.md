# Book Onboarding Workflow

How to add a new book to the reading data companion project.

## 1. Create the book directory structure

Choose a kebab-case slug for the book (e.g., `the-grid`, `energy-democracy`).

```
mkdir -p {book-slug}/brainstorming/chapters
mkdir -p {book-slug}/brainstorming/side
mkdir -p data/raw/{book-slug}
```

## 2. Add metadata

Copy the metadata template and fill in book details:

```
cp templates/metadata.yaml {book-slug}/metadata.yaml
```

Edit to include:
- Title, author, publication year
- Chapter list with slugs and titles
- Key themes you want to explore
- General data sources

## 3. Add progress tracker

```
cp templates/progress.md {book-slug}/progress.md
```

Update the chapter table to match your book's chapters.

## 4. Per-chapter workflow

As you read each chapter:

1. **Create chapter directories:**
   ```
   mkdir -p {book-slug}/brainstorming/chapters/{chapter-slug}
   mkdir -p data/raw/{book-slug}/{chapter-slug}
   ```

2. **Brainstorm visualizations:** Add notes to `brainstorming/chapters/{chapter-slug}/`

3. **Gather data:** Store raw datasets in `data/raw/{book-slug}/{chapter-slug}/`

4. **Update progress:** Check off stages in `progress.md`

## Directory structure overview

```
{book-slug}/
├── metadata.yaml              # Book info, chapters, themes
├── progress.md                # Reading/building progress
└── brainstorming/
    ├── chapters/
    │   └── {chapter-slug}/    # Visualization ideas per chapter
    └── side/                  # Tangential project ideas

data/raw/{book-slug}/
└── {chapter-slug}/            # Raw datasets per chapter
```

## Side projects

Sometimes a book inspires ideas beyond chapter-specific visualizations. Store these in `{book-slug}/brainstorming/side/` with their own subdirectories.
