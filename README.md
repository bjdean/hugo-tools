# Hugo Tools

A toolkit for managing Hugo sites.

## Features

Hugo Tools provides a unified command-line interface for common Hugo site management tasks:

- **Datetime Sync**: Synchronize file modification times with frontmatter dates (makes file listings show posts in chronological order)
- **Tag/Metadata Management**: Bulk add, remove, or modify tags, categories, and custom metadata fields
- **WordPress Import**: Convert WordPress XML exports to Hugo-formatted markdown files

## Installation

### From PyPI (once published)

```bash
pip install hugotools
```

### From Source

```bash
git clone https://github.com/bjdean/hugo-tools.git
cd hugo-tools
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/bjdean/hugo-tools.git
cd hugo-tools
pip install -e ".[dev]"
```

## Quick Start

All commands follow the pattern: `hugotools <command> [options]`

### Sync File Dates

```bash
# Sync all posts
hugotools datetime --all

# Sync specific posts
hugotools datetime --path content/posts/2023-01-01-mypost.md

# Preview changes without modifying files
hugotools datetime --all --dry-run
```

### Manage Tags

```bash
# Add tags to all posts
hugotools tag --all --add "python,tutorial"

# Remove tags from posts matching a pattern
hugotools tag --title "docker" --remove "draft"

# Work with categories instead of tags
hugotools tag --all --categories --add "Technology"

# List all tags in use
hugotools tag --all --dump
```

### Import from WordPress

```bash
# Convert WordPress export to Hugo posts
hugotools import wordpress-export.xml --output-dir content/posts

# Preview conversion without writing files
hugotools import wordpress-export.xml --dry-run

# Limit conversion for testing
hugotools import wordpress-export.xml --limit 5
```

## Command Reference

### `hugotools datetime`

Synchronizes file modification times with Hugo frontmatter dates. This is useful for making file listings show posts in chronological order based on their publication date.

**Options:**
- `--all`: Select all posts
- `--title PATTERN`: Select posts with title matching PATTERN
- `--fromdate YYYY-MM-DD`: Select posts from this date onwards
- `--todate YYYY-MM-DD`: Select posts up to this date
- `--path PATH [PATH ...]`: Select specific posts by path
- `--content-dir PATH`: Hugo content directory (default: content/posts)
- `--dry-run`: Preview changes without modifying files

**Examples:**
```bash
# Sync all posts
hugotools datetime --all

# Sync posts from 2023
hugotools datetime --fromdate 2023-01-01 --todate 2023-12-31

# Sync specific file
hugotools datetime --path content/posts/my-post.md
```

### `hugotools tag`

Manages tags, categories, and other metadata fields in Hugo post frontmatter.

**Field Selection:**
- (default): Operate on `tags`
- `--categories`: Operate on `categories`
- `--custom-list FIELD`: Operate on a custom list field
- `--custom-label FIELD`: Operate on a custom single-value field

**Operations:**
- `--add TAG[,TAG,...]`: Add items (for list fields)
- `--remove TAG[,TAG,...]`: Remove items (for list fields) or remove field entirely (for label fields)
- `--set VALUE`: Set value (for label fields only)
- `--dump`: Display current values without modifying

**Post Selection:**
- `--all`: Select all posts
- `--title PATTERN`: Select posts with title matching PATTERN
- `--text PATTERN`: Select posts with PATTERN in content or frontmatter
- `--fromdate YYYY-MM-DD`: Select posts from this date onwards
- `--todate YYYY-MM-DD`: Select posts up to this date
- `--path PATH [PATH ...]`: Select specific posts by path

**Common Options:**
- `--content-dir PATH`: Hugo content directory (default: content/posts)
- `--dry-run`: Preview changes without modifying files

**Examples:**
```bash
# Add tags to all posts
hugotools tag --all --add "python,tutorial"

# Remove a tag from posts with specific title
hugotools tag --title "Introduction" --remove "draft"

# Add categories
hugotools tag --all --categories --add "Technology,Programming"

# Set a custom field value
hugotools tag --title "My Post" --custom-label status --set "published"

# List all tags currently in use
hugotools tag --all --dump

# List categories from posts containing "docker"
hugotools tag --text "docker" --categories --dump
```

### `hugotools import`

Converts WordPress XML export files to Hugo-formatted markdown posts.

**Arguments:**
- `xml_file`: WordPress XML export file (required)

**Options:**
- `--output-dir PATH`: Output directory for converted posts (default: wordpress-export)
- `--dry-run`: Preview conversion without writing files
- `--limit N`: Limit number of posts to convert (useful for testing)

**Features:**
- Converts HTML content to Markdown
- Preserves categories and tags
- Handles code blocks and images
- Generates Hugo-compatible URLs
- Sets file modification times to match post dates
- Detects and reports unconverted HTML tags

**Examples:**
```bash
# Convert entire WordPress export
hugotools import wordpress-export.xml --output-dir content/posts

# Preview first 5 posts
hugotools import wordpress-export.xml --limit 5 --dry-run

# Convert to custom directory
hugotools import my-blog.xml --output-dir imported-posts
```

## Common Workflows

### Bulk Tagging Workflow

```bash
# 1. See what tags are currently in use
hugotools tag --all --dump

# 2. Add new tags to relevant posts
hugotools tag --text "python" --add "programming,python"

# 3. Verify changes
hugotools tag --text "python" --dump
```

### WordPress Migration Workflow

```bash
# 1. Export from WordPress (Tools → Export → All content)

# 2. Test conversion with a few posts
hugotools import wordpress-export.xml --limit 10 --dry-run

# 3. Convert all posts
hugotools import wordpress-export.xml --output-dir content/posts

# 4. Review posts with HTML that needs manual cleanup
# (tool will report these at the end)

# 5. Sync file dates to match publication dates
hugotools datetime --all --content-dir content/posts
```

### Organizing Content by Date

```bash
# Add "archive" category to old posts
hugotools tag --todate 2020-12-31 --categories --add "Archive"

# Remove draft tags from published posts
hugotools tag --fromdate 2023-01-01 --remove "draft"

# Sync file timestamps
hugotools datetime --all
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
ruff src/
```

## Requirements

- Python 3.8+
- PyYAML
- beautifulsoup4
- markdownify

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Brad Dean (hugo-tools@bjdean.id.au)

## Links

- GitHub: https://github.com/bjdean/hugo-tools
- Issues: https://github.com/bjdean/hugo-tools/issues
