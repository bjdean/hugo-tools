#!/usr/bin/env python3
"""
Convert WordPress XML export to Hugo markdown posts.

This script processes a standard WordPress XML export file and converts
it to Hugo-formatted markdown files with proper frontmatter.

Features:
- Parses WordPress WXR (WordPress eXtended RSS) format
- Converts HTML content to Markdown
- Extracts categories, tags, and metadata
- Handles code blocks and images
- Skips drafts, attachments, and other non-post items
- Creates proper Hugo frontmatter
- Generates clean URLs based on post slugs
"""

import argparse
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import unquote

import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md


# WordPress XML namespaces
NAMESPACES = {
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wfw': 'http://wellformedweb.org/CommentAPI/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'wp': 'http://wordpress.org/export/1.2/',
}


class WordPressPost:
    """Represents a WordPress post with all its metadata."""

    def __init__(self, item: ET.Element):
        self.item = item
        self.title = self._get_text('title')
        self.link = self._get_text('link')
        self.pub_date = self._get_text('pubDate')
        self.creator = self._get_text('dc:creator', NAMESPACES)
        self.guid = self._get_text('guid')
        self.description = self._get_text('description')
        self.content = self._get_text('content:encoded', NAMESPACES)
        self.excerpt = self._get_text('excerpt:encoded', NAMESPACES)

        # WordPress-specific fields
        self.post_id = self._get_text('wp:post_id', NAMESPACES)
        self.post_date = self._get_text('wp:post_date', NAMESPACES)
        self.post_date_gmt = self._get_text('wp:post_date_gmt', NAMESPACES)
        self.post_modified = self._get_text('wp:post_modified', NAMESPACES)
        self.post_name = self._get_text('wp:post_name', NAMESPACES)
        self.status = self._get_text('wp:status', NAMESPACES)
        self.post_parent = self._get_text('wp:post_parent', NAMESPACES)
        self.post_type = self._get_text('wp:post_type', NAMESPACES)
        self.is_sticky = self._get_text('wp:is_sticky', NAMESPACES)

        # Categories and tags
        self.categories = []
        self.tags = []
        self._parse_taxonomies()

    def _get_text(self, tag: str, namespaces: Optional[Dict] = None) -> str:
        """Get text content from XML element."""
        elem = self.item.find(tag, namespaces or {})
        return elem.text.strip() if elem is not None and elem.text else ''

    def _parse_taxonomies(self):
        """Extract categories and tags from category elements."""
        for cat_elem in self.item.findall('category'):
            domain = cat_elem.get('domain', '')
            nicename = cat_elem.get('nicename', '')
            text = cat_elem.text or ''

            if domain == 'category' and text:
                self.categories.append(text)
            elif domain == 'post_tag' and text:
                self.tags.append(text)

    def should_export(self) -> bool:
        """Check if this post should be exported."""
        # Only export published posts (not drafts, private, etc.)
        if self.status != 'publish':
            return False

        # Only export actual posts (not pages, attachments, nav items, etc.)
        if self.post_type != 'post':
            return False

        # Must have content
        if not self.content:
            return False

        return True

    def get_hugo_date(self) -> str:
        """Convert WordPress date to Hugo-compatible ISO format."""
        try:
            # Parse WordPress date format: 2019-02-05 23:30:40
            dt = datetime.strptime(self.post_date, '%Y-%m-%d %H:%M:%S')
            # Return ISO format with timezone
            return dt.isoformat() + '+00:00'
        except (ValueError, TypeError):
            # Fallback to current time if parsing fails
            return datetime.now().isoformat() + '+00:00'

    def get_hugo_url(self) -> str:
        """Generate Hugo-compatible URL from post link.

        Extracts the path from the WordPress link field, preserving
        the date-based structure (e.g., /2022/12/asterisk-intended/)
        and decoding URL-encoded characters (e.g., %cf%80 -> π)
        """
        if self.link:
            # Extract path from URL
            # Example: https://blog.bjdean.id.au/2022/12/asterisk-intended/ -> /2022/12/asterisk-intended/
            match = re.search(r'https?://[^/]+(/.*)', self.link)
            if match:
                # Decode URL-encoded characters (e.g., %cf%80 -> π)
                return unquote(match.group(1))

        # Fallback to post_name or post_id
        if self.post_name:
            return f'/{self.post_name}/'
        return f'/{self.post_id}/'

    def get_timestamp(self) -> Optional[float]:
        """Get Unix timestamp from post date for setting file mtime."""
        try:
            # Parse WordPress date format: 2019-02-05 23:30:40
            dt = datetime.strptime(self.post_date, '%Y-%m-%d %H:%M:%S')
            return dt.timestamp()
        except (ValueError, TypeError):
            return None


def clean_html_entities(text: str) -> str:
    """Convert HTML entities to proper Unicode characters."""
    # Unescape HTML entities
    text = html.unescape(text)

    # Handle any remaining numeric entities
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)

    return text


def convert_code_blocks(text: str) -> str:
    """Convert HTML code blocks to Markdown code fences.

    IMPORTANT: This must be called BEFORE clean_html_entities to preserve
    HTML-like syntax in code blocks (e.g., Apache config with <VirtualHost>).

    Returns a tuple of (modified_text, list_of_code_blocks) where code blocks
    are replaced with placeholders.
    """
    code_blocks = []

    # Use regex to extract <pre> blocks with their raw content
    # This preserves &lt; &gt; entities which we'll convert later
    def replace_pre_block(match):
        pre_content = match.group(1)

        # Check if there's a <code> tag inside
        code_match = re.search(r'<code([^>]*)>(.*?)</code>', pre_content, re.DOTALL)

        if code_match:
            attrs = code_match.group(1)
            code_content = code_match.group(2)

            # Try to detect language from class
            lang = ''
            class_match = re.search(r'class=["\']([^"\']*)["\']', attrs)
            if class_match:
                classes = class_match.group(1).split()
                for cls in classes:
                    if cls.startswith('language-'):
                        lang = cls.replace('language-', '')
                    elif cls in ['python', 'bash', 'javascript', 'js', 'perl', 'shell', 'sh', 'go', 'rust', 'java', 'c', 'cpp']:
                        lang = cls
        else:
            code_content = pre_content
            lang = ''

        # Unescape HTML entities in code content
        code_text = html.unescape(code_content)

        # Store the code block
        code_block = f'\n```{lang}\n{code_text}\n```\n'
        code_blocks.append(code_block)

        # Return placeholder that won't be touched by markdownify
        return f'___CODEBLOCK_{len(code_blocks)-1}___'

    # Replace all <pre>...</pre> blocks with placeholders
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', replace_pre_block, text, flags=re.DOTALL | re.IGNORECASE)

    return text, code_blocks


def convert_images(text: str) -> str:
    """Convert HTML image tags and WordPress caption shortcodes to Markdown."""
    soup = BeautifulSoup(text, 'html.parser')

    # Handle WordPress caption shortcodes before processing HTML
    # Pattern: [caption ...]<img>...[/caption]
    text_str = str(soup)
    # Remove [caption ...] opening tags
    text_str = re.sub(r'\[caption[^\]]*\]', '', text_str)
    # Remove [/caption] closing tags
    text_str = re.sub(r'\[/caption\]', '', text_str)
    soup = BeautifulSoup(text_str, 'html.parser')

    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')

        # Remove loading="lazy" and other WordPress-specific attributes
        # For srcset (responsive images), just use the src for now

        # Convert to markdown
        md_img = f"![{alt}]({src})"
        img.replace_with(md_img)

    # Remove figure wrappers
    for figure in soup.find_all('figure'):
        # Extract content and unwrap
        figure.unwrap()

    return str(soup)


def detect_stray_html(text: str) -> List[str]:
    """Detect any remaining HTML tags in the content."""
    # Split content into code blocks and regular content
    # Remove everything between ``` markers (code blocks)
    text_without_code = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Find all HTML-like tags outside code blocks
    tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>', text_without_code)

    # Filter out common false positives and valid markdown/HTML-like patterns
    # - Single letters/numbers (likely from code or special syntax)
    # - Protocol handlers (http, https, ftp, etc.)
    excluded_patterns = {'codeblock', 'http', 'https', 'ftp', 'mailto'}
    tags = [tag for tag in tags if tag.lower() not in excluded_patterns and not tag.isdigit()]

    # Also filter out single character tags
    tags = [tag for tag in tags if len(tag) > 1]

    return list(set(tags))  # Return unique tags


def create_hugo_frontmatter(post: WordPressPost) -> Dict:
    """Create Hugo frontmatter dictionary from WordPress post."""
    frontmatter = {
        'title': post.title,
        'date': post.get_hugo_date(),
        'url': post.get_hugo_url(),
    }

    # Add categories if present
    if post.categories:
        frontmatter['categories'] = post.categories

    # Add tags if present
    if post.tags:
        frontmatter['tags'] = post.tags

    # Add excerpt if present
    if post.excerpt:
        excerpt_clean = clean_html_entities(post.excerpt)
        excerpt_clean = BeautifulSoup(excerpt_clean, 'html.parser').get_text()
        frontmatter['description'] = excerpt_clean.strip()

    return frontmatter


def convert_post(post: WordPressPost) -> str:
    """Convert a WordPress post to Hugo markdown format."""
    # Create frontmatter
    frontmatter = create_hugo_frontmatter(post)

    # Clean content - NOTE THE ORDER IS CRITICAL:
    # 1. First extract and convert code blocks (while entities are still &lt; etc)
    #    This replaces them with placeholders
    # 2. Then clean entities in the rest of the content
    # 3. Then do general markdown conversion (won't affect placeholders)
    # 4. Finally restore the code blocks
    content = post.content

    # Step 1: Extract and convert code blocks (returns text with placeholders and list of blocks)
    content, code_blocks = convert_code_blocks(content)

    # Step 2: DO NOT clean HTML entities yet - leave them as &lt; and &gt;
    # This way markdownify will handle them properly

    # Step 3: Do the rest of the conversion (images, markdown, etc.)
    content = convert_images(content)

    # Use markdownify for general HTML to Markdown conversion
    # This will handle &lt; and &gt; entities properly
    content = md(
        content,
        heading_style="ATX",
        bullets="-",
        strong_em_symbol="*",
        escape_asterisks=False,
        escape_underscores=False
    )

    # NOW clean remaining HTML entities (after markdownify won't be confused by them)
    content = clean_html_entities(content)

    # Step 4: Restore code blocks from placeholders
    for i, code_block in enumerate(code_blocks):
        content = content.replace(f'___CODEBLOCK_{i}___', code_block)

    # Clean up excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Clean up &nbsp; that might remain
    content = content.replace('&nbsp;', ' ')

    # Remove WordPress shortcodes
    protected_links = []
    def protect_link(match):
        protected_links.append(match.group(0))
        return f"___LINK_{len(protected_links)-1}___"

    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', protect_link, content)
    content = re.sub(r'\[/?[\w_-]+[^\]]*\]', '', content)

    for i, link in enumerate(protected_links):
        content = content.replace(f"___LINK_{i}___", link)

    # Clean up any remaining HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Fix markdown links that got mangled
    content = re.sub(r'\]\s+\(', '](', content)

    # Remove extra escaping of underscores
    content = re.sub(r'([a-zA-Z0-9])\\_([a-zA-Z0-9])', r'\1_\2', content)

    # Final cleanup
    content = re.sub(r' +\n', '\n', content)

    content = content.strip()

    # Build the markdown file
    output = "---\n"
    output += yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    output += "---\n\n"
    output += content

    return output


def parse_wordpress_xml(xml_path: Path) -> List[WordPressPost]:
    """Parse WordPress XML export and extract posts."""
    print(f"Parsing WordPress XML export: {xml_path}")

    # Parse XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Find all items
    items = root.findall('.//item')
    print(f"Found {len(items)} items in export")

    # Convert to WordPressPost objects
    posts = []
    for item in items:
        post = WordPressPost(item)
        if post.should_export():
            posts.append(post)

    print(f"Found {len(posts)} publishable posts")
    return posts


def generate_filename(post: WordPressPost) -> str:
    """Generate Hugo-compatible filename for post."""
    # Use post slug if available
    if post.post_name:
        filename = post.post_name
    else:
        # Fallback to sanitized title
        filename = post.title.lower()
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '-', filename)

    # Ensure .md extension
    if not filename.endswith('.md'):
        filename += '.md'

    return filename


def run(args=None):
    """Run the WordPress import command."""
    parser = argparse.ArgumentParser(
        prog='hugotools import',
        description='Convert WordPress XML export to Hugo markdown posts'
    )
    parser.add_argument(
        'xml_file',
        type=Path,
        help='WordPress XML export file'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('wordpress-export'),
        help='Output directory for Hugo posts (default: wordpress-export)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without writing files'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of posts to convert (for testing)'
    )

    parsed_args = parser.parse_args(args)

    # Validate input
    if not parsed_args.xml_file.exists():
        print(f"Error: Input file {parsed_args.xml_file} does not exist", file=sys.stderr)
        return 1

    # Parse WordPress export
    try:
        posts = parse_wordpress_xml(parsed_args.xml_file)
    except Exception as e:
        print(f"Error parsing WordPress XML: {e}", file=sys.stderr)
        return 1

    if not posts:
        print("No posts found to export")
        return 0

    # Apply limit if specified
    if parsed_args.limit:
        posts = posts[:parsed_args.limit]
        print(f"Limiting export to {len(posts)} posts")

    # Statistics
    stats = {
        'total': len(posts),
        'success': 0,
        'error': 0,
        'skipped': 0,
    }

    # Track files with issues
    files_with_stray_html = []

    # Create output directory
    if not parsed_args.dry_run:
        parsed_args.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {parsed_args.output_dir}")

    print(f"\n{'='*60}")
    print(f"Converting {len(posts)} posts...")
    print(f"{'='*60}\n")

    # Convert each post
    for i, post in enumerate(posts, 1):
        try:
            filename = generate_filename(post)
            output_path = parsed_args.output_dir / filename

            # Convert post
            markdown = convert_post(post)

            # Check for stray HTML tags
            stray_tags = detect_stray_html(markdown)
            if stray_tags:
                files_with_stray_html.append({
                    'filename': filename,
                    'title': post.title,
                    'tags': stray_tags
                })

            # Progress indicator
            print(f"[{i}/{len(posts)}] {post.title}")
            print(f"  -> {filename}")
            print(f"  Categories: {', '.join(post.categories) if post.categories else 'None'}")
            print(f"  Tags: {', '.join(post.tags) if post.tags else 'None'}")
            print(f"  Date: {post.post_date}")
            if stray_tags:
                print(f"  WARNING: Contains HTML tags: {', '.join(stray_tags)}")

            if parsed_args.dry_run:
                print(f"  [DRY RUN] Would write to: {output_path}")
                print(f"  Content preview (first 200 chars):")
                preview = markdown[:200].replace('\n', ' ')
                print(f"    {preview}...")
            else:
                # Write file
                output_path.write_text(markdown, encoding='utf-8')

                # Set file modification time to match post date
                timestamp = post.get_timestamp()
                if timestamp:
                    os.utime(output_path, (timestamp, timestamp))

                print(f"  Written to: {output_path}")

            stats['success'] += 1
            print()

        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            stats['error'] += 1
            print()

    # Print summary
    print(f"{'='*60}")
    print(f"CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"Total posts:            {stats['total']}")
    print(f"Successfully converted: {stats['success']}")
    print(f"Errors:                 {stats['error']}")
    print(f"{'='*60}")

    # Report files with stray HTML
    if files_with_stray_html:
        print(f"\n{'='*60}")
        print(f"FILES REQUIRING MANUAL REVIEW")
        print(f"{'='*60}")
        print(f"\nThe following {len(files_with_stray_html)} file(s) contain HTML tags that may need manual cleanup:\n")
        for file_info in files_with_stray_html:
            print(f"  {file_info['filename']}")
            print(f"    Title: {file_info['title']}")
            print(f"    HTML tags found: {', '.join(sorted(file_info['tags']))}")
            print()
        print(f"{'='*60}")

    if parsed_args.dry_run:
        print("\nThis was a DRY RUN. Run without --dry-run to write files.")

    return 0 if stats['error'] == 0 else 1


if __name__ == '__main__':
    sys.exit(run())
