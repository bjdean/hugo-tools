# Hugo Tools Documentation

Complete documentation for the Hugo Tools package.

## Table of Contents

- [Installation](#installation)
- [Commands](#commands)
  - [datetime](#datetime-command)
  - [tag](#tag-command)
  - [import](#import-command)
- [Common Workflows](#common-workflows)
- [API Reference](#api-reference)

## Installation

### From PyPI

```bash
pip install hugotools
```

### From Source

```bash
git clone https://github.com/bjdean/hugo-tools.git
cd hugo-tools
pip install -e .
```

### Development Setup

```bash
git clone https://github.com/bjdean/hugo-tools.git
cd hugo-tools
pip install -e ".[dev]"
```

## Commands

### datetime Command

Synchronizes file modification times with Hugo frontmatter dates.

**Why use this?**
- File browsers and `ls -lt` will show posts in chronological order
- Easier to identify recent vs old posts visually
- Helps with backup and sync tools that use file modification times

**Usage:**
```bash
hugotools datetime [OPTIONS]
```

**Post Selection Options:**
- `--all` - Select all posts
- `--title PATTERN` - Select posts with title matching PATTERN (case-insensitive)
- `--fromdate YYYY-MM-DD` - Select posts from this date onwards
- `--todate YYYY-MM-DD` - Select posts up to this date
- `--path PATH [PATH...]` - Select specific posts by file path

**Other Options:**
- `--content-dir PATH` - Hugo content directory (default: content/posts)
- `--dry-run` - Show what would change without modifying files

**Examples:**

```bash
# Sync all posts in default directory
hugotools datetime --all

# Sync posts from a specific year
hugotools datetime --fromdate 2023-01-01 --todate 2023-12-31

# Sync specific post
hugotools datetime --path content/posts/my-post.md

# Preview changes first
hugotools datetime --all --dry-run

# Sync posts with "docker" in title
hugotools datetime --title docker

# Sync posts in custom directory
hugotools datetime --all --content-dir content/blog
```

### tag Command

Manages tags, categories, and other metadata fields in Hugo posts.

**Why use this?**
- Bulk add/remove tags across many posts
- Reorganize content taxonomy
- Add custom metadata fields
- Audit which tags are in use

**Usage:**
```bash
hugotools tag [FIELD OPTIONS] [POST SELECTION] [OPERATIONS] [OTHER OPTIONS]
```

**Field Selection (choose one):**
- (default) - Operate on `tags` field
- `--categories` - Operate on `categories` field
- `--custom-list FIELD` - Operate on custom list field (e.g., `keywords`, `authors`)
- `--custom-label FIELD` - Operate on custom single-value field (e.g., `status`, `series`)

**Post Selection:**
- `--all` - Select all posts
- `--title PATTERN` - Match title
- `--text PATTERN` - Match anywhere in frontmatter or content
- `--fromdate YYYY-MM-DD` - Posts from date
- `--todate YYYY-MM-DD` - Posts until date
- `--path PATH [PATH...]` - Specific files

**Operations:**

For list fields (tags, categories, custom-list):
- `--add TAG[,TAG,...]` - Add items (comma-separated)
- `--remove TAG[,TAG,...]` - Remove items (comma-separated)
- `--dump` - Display current values

For label fields (custom-label):
- `--set VALUE` - Set the value
- `--remove` - Remove the field entirely
- `--dump` - Display current values

**Other Options:**
- `--content-dir PATH` - Content directory (default: content/posts)
- `--dry-run` - Preview without modifying

**Examples:**

```bash
# Add tags to all posts
hugotools tag --all --add "hugo,static-site"

# Remove draft tag from posts
hugotools tag --all --remove "draft"

# Add tags to posts matching pattern
hugotools tag --title "python" --add "programming,tutorial"

# Work with categories
hugotools tag --all --categories --add "Technology"

# Set a custom label
hugotools tag --path my-post.md --custom-label series --set "Getting Started"

# Remove a custom field
hugotools tag --all --custom-label deprecated --remove

# List all tags in use
hugotools tag --all --dump

# List categories from posts about docker
hugotools tag --text docker --categories --dump

# Dry run to preview changes
hugotools tag --all --add "test" --dry-run
```

### import Command

Converts WordPress XML export to Hugo markdown posts.

**Why use this?**
- Migrate from WordPress to Hugo
- Convert HTML to Markdown automatically
- Preserve post metadata, categories, and tags
- Set file modification times to match publication dates

**Usage:**
```bash
hugotools import XML_FILE [OPTIONS]
```

**Arguments:**
- `XML_FILE` - WordPress XML export file (required)

**Options:**
- `--output-dir PATH` - Output directory (default: wordpress-export)
- `--dry-run` - Preview conversion without writing files
- `--limit N` - Limit posts to convert (useful for testing)

**Features:**
- Converts HTML to Markdown
- Preserves frontmatter (title, date, categories, tags)
- Handles code blocks with syntax highlighting
- Converts images to Markdown format
- Detects and reports unconverted HTML
- Generates Hugo-compatible URLs
- Sets file timestamps to match post dates

**WordPress Export Process:**
1. In WordPress admin: Tools → Export
2. Select "All content" or "Posts"
3. Download the XML file
4. Run `hugotools import`

**Examples:**

```bash
# Basic import
hugotools import wordpress-export.xml

# Import to specific directory
hugotools import wordpress-export.xml --output-dir content/posts

# Test with first 5 posts
hugotools import wordpress-export.xml --limit 5 --dry-run

# Full import with custom output
hugotools import my-blog.xml --output-dir imported-content
```

**Post-Import Checklist:**
1. Review posts with HTML warnings
2. Check image links are correct
3. Verify code blocks formatted properly
4. Test internal links
5. Run `hugotools datetime --all` to sync file times

## Common Workflows

### Migrating from WordPress

```bash
# 1. Export from WordPress (Tools → Export)

# 2. Test conversion with a few posts
hugotools import wordpress.xml --limit 10 --dry-run

# 3. Do full conversion
hugotools import wordpress.xml --output-dir content/posts

# 4. Review and fix any HTML warnings
# (Check the conversion summary)

# 5. Sync file timestamps
hugotools datetime --all --content-dir content/posts

# 6. Add any missing categorization
hugotools tag --all --add "imported-from-wordpress"
```

### Reorganizing Content

```bash
# Audit current tags
hugotools tag --all --dump

# Remove old/unused tags
hugotools tag --all --remove "old-tag,deprecated"

# Add new organizational tags
hugotools tag --text "tutorial" --add "learning,guide"
hugotools tag --text "reference" --add "documentation"

# Update categories
hugotools tag --all --categories --add "Blog"

# Verify changes
hugotools tag --all --dump
```

### Bulk Updates by Date

```bash
# Archive old posts
hugotools tag --todate 2020-12-31 --categories --add "Archive"

# Mark recent posts
hugotools tag --fromdate 2024-01-01 --add "recent,2024"

# Update status field
hugotools tag --all --custom-label status --set "published"
```

### Maintaining File Timestamps

```bash
# After editing posts, restore original publish dates
hugotools datetime --all

# Sync only recent posts
hugotools datetime --fromdate 2024-01-01

# Sync specific post after editing
hugotools datetime --path content/posts/my-edited-post.md
```

## API Reference

### HugoPost Class

Represents a single Hugo post with frontmatter and content.

```python
from hugotools.common import HugoPost
from pathlib import Path

post = HugoPost(Path('content/posts/my-post.md'))

# Access frontmatter
title = post.get_title()
date = post.get_date()
tags = post.get_metadata_list('tags')
author = post.get_metadata_label('author')

# Modify metadata
post.set_metadata_list('tags', ['python', 'hugo'])
post.set_metadata_label('status', 'published')

# Save changes
post.save()
```

### HugoPostManager Class

Manages multiple Hugo posts with filtering capabilities.

```python
from hugotools.common import HugoPostManager
from pathlib import Path
from datetime import datetime

manager = HugoPostManager(Path('content/posts'))
manager.load_posts()

# Filter posts
recent_posts = manager.filter_posts(
    from_date=datetime(2024, 1, 1)
)

python_posts = manager.filter_posts(
    title_pattern='python'
)

specific_posts = manager.filter_posts(
    paths=['content/posts/post1.md', 'content/posts/post2.md']
)
```

### Command Modules

Each command can be imported and used programmatically:

```python
from hugotools.commands import datetime, tag, import_wordpress

# Run commands with custom arguments
datetime.run(['--all', '--dry-run'])
tag.run(['--all', '--add', 'python'])
import_wordpress.run(['export.xml', '--output-dir', 'posts'])
```

## Troubleshooting

### "No posts selected"

Make sure your selection criteria match posts:
- Check `--content-dir` points to correct directory
- Verify posts have frontmatter (YAML between `---` markers)
- Use `--all` to select everything
- Try broader date ranges or patterns

### "No valid date in frontmatter"

The `datetime` command requires posts to have a `date` field:

```yaml
---
title: My Post
date: 2024-01-15 10:30:00
---
```

### Import warnings about HTML tags

Some WordPress HTML may not convert perfectly. Common issues:
- Complex tables
- Custom shortcodes
- Embedded widgets
- Custom CSS/styling

Review these posts manually and update as needed.

### Permission errors

Ensure you have write permissions:
- File is not read-only
- Directory is writable
- No other program has file open

## Contributing

See the main README.md for contribution guidelines.

## License

MIT License - see LICENSE file
