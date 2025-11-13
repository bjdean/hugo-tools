#!/usr/bin/env python3
"""
Hugo Common Library

Shared utilities for working with Hugo markdown post files.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Import tomlkit for style-preserving TOML writing
import tomlkit


class HugoPost:
    """Represents a Hugo post with frontmatter and content."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.frontmatter: Dict = {}
        self.content: str = ""
        self.frontmatter_raw: str = ""
        self.has_frontmatter: bool = False
        self.frontmatter_format: str = "yaml"  # Track format: yaml, toml, or json
        self.toml_document = None  # Store tomlkit document to preserve comments
        self._parse()

    def _parse(self):
        """Parse the Hugo post file to extract frontmatter and content."""
        with open(self.file_path, encoding="utf-8") as f:
            text = f.read()

        # Try YAML frontmatter (delimited by ---)
        yaml_pattern = r"^---\s*\n(.*?\n)---\s*\n(.*)$"
        match = re.match(yaml_pattern, text, re.DOTALL)

        if match:
            self.has_frontmatter = True
            self.frontmatter_format = "yaml"
            self.frontmatter_raw = match.group(1)
            self.content = match.group(2)
            try:
                self.frontmatter = yaml.safe_load(self.frontmatter_raw) or {}
            except yaml.YAMLError as e:
                print(f"Warning: Failed to parse YAML in {self.file_path}: {e}")
                self.frontmatter = {}
            return

        # Try TOML frontmatter (delimited by +++)
        toml_pattern = r"^\+\+\+\s*\n(.*?\n)\+\+\+\s*\n(.*)$"
        match = re.match(toml_pattern, text, re.DOTALL)

        if match:
            self.has_frontmatter = True
            self.frontmatter_format = "toml"
            self.frontmatter_raw = match.group(1)
            self.content = match.group(2)
            try:
                # Use tomlkit to preserve comments and formatting
                self.toml_document = tomlkit.loads(self.frontmatter_raw)
                # Also keep a dict version for easy access
                self.frontmatter = dict(self.toml_document)
            except Exception as e:
                print(f"Warning: Failed to parse TOML in {self.file_path}: {e}")
                self.frontmatter = {}
                self.toml_document = None
            return

        # Try JSON frontmatter (starts with { and ends with })
        json_pattern = r"^(\{[\s\S]*?\n\})\s*\n(.*)$"
        match = re.match(json_pattern, text, re.DOTALL)

        if match:
            self.has_frontmatter = True
            self.frontmatter_format = "json"
            self.frontmatter_raw = match.group(1)
            self.content = match.group(2)
            try:
                self.frontmatter = json.loads(self.frontmatter_raw)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON in {self.file_path}: {e}")
                self.frontmatter = {}
            return

        # No frontmatter found
        self.content = text

    def get_metadata_list(self, field: str) -> list:
        """Get a metadata field as a list (handles both single values and lists)."""
        value = self.frontmatter.get(field, [])
        if isinstance(value, str):
            return [value]
        elif isinstance(value, list):
            return value
        return []

    def set_metadata_list(self, field: str, values: list):
        """Set a metadata field with a list of values."""
        if not values:
            # Remove the field if empty
            if field in self.frontmatter:
                del self.frontmatter[field]
        else:
            self.frontmatter[field] = values

    def get_metadata_label(self, field: str) -> Optional[str]:
        """Get a metadata field as a single value."""
        value = self.frontmatter.get(field)
        if value is None:
            return None
        return str(value)

    def set_metadata_label(self, field: str, value: Optional[str]):
        """Set a metadata field with a single value."""
        if value is None:
            # Remove the field if None
            if field in self.frontmatter:
                del self.frontmatter[field]
        else:
            self.frontmatter[field] = value

    def get_title(self) -> str:
        """Get the post title."""
        return self.frontmatter.get("title", "")

    def get_date(self) -> Optional[datetime]:
        """Get the post date."""
        date_str = self.frontmatter.get("date", "")
        if not date_str:
            return None

        # Try to parse various date formats
        date_str = str(date_str)
        for fmt in ["%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z"]:
            try:
                # Remove timezone info for simplicity
                date_str_clean = date_str.split("+")[0].strip().strip("'\"")
                return datetime.strptime(date_str_clean, fmt.split("%z")[0].strip())
            except ValueError:
                continue
        return None

    def get_full_text(self) -> str:
        """Get the full text of the post (frontmatter + content)."""
        return f"{self.frontmatter_raw}\n{self.content}"

    def save(self):
        """Save the post back to disk, preserving the original frontmatter format."""
        # Serialize frontmatter based on the original format
        if self.frontmatter_format == "yaml":
            frontmatter_str = yaml.dump(
                self.frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
            delimiter = "---"
        elif self.frontmatter_format == "toml":
            # Use tomlkit to preserve comments and formatting
            if self.toml_document is not None:
                # Update the tomlkit document with any changes from self.frontmatter
                self._update_toml_document()
                frontmatter_str = tomlkit.dumps(self.toml_document)
            else:
                # Fallback if toml_document is not available
                frontmatter_str = tomlkit.dumps(self.frontmatter)
            delimiter = "+++"
        elif self.frontmatter_format == "json":
            frontmatter_str = json.dumps(self.frontmatter, indent=2, ensure_ascii=False)
            # JSON doesn't use delimiters in the same way - the braces are part of the JSON
            # Write the file
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(frontmatter_str)
                f.write("\n")
                f.write(self.content)
            return
        else:
            # Default to YAML if format is unknown
            frontmatter_str = yaml.dump(
                self.frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
            delimiter = "---"

        # Write the file with delimiters
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(f"{delimiter}\n")
            f.write(frontmatter_str)
            f.write(f"{delimiter}\n")
            f.write(self.content)

    def _update_toml_document(self):
        """Update the tomlkit document with changes from self.frontmatter."""
        if self.toml_document is None:
            return

        # Get keys that exist in both
        doc_keys = set(self.toml_document.keys())
        fm_keys = set(self.frontmatter.keys())

        # Update existing keys and add new keys
        for key in fm_keys:
            self.toml_document[key] = self.frontmatter[key]

        # Remove keys that are no longer in frontmatter
        for key in doc_keys - fm_keys:
            del self.toml_document[key]

    def _prepare_for_toml(self, data):
        """Prepare data for TOML serialization by converting datetime objects."""
        if isinstance(data, dict):
            return {k: self._prepare_for_toml(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_for_toml(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        return data


class HugoPostManager:
    """Base manager for Hugo posts with common loading and filtering functionality."""

    def __init__(self, content_dir: Path = Path("content/posts")):
        self.content_dir = content_dir
        self.posts: List[HugoPost] = []

    def load_posts(self):
        """Load all markdown posts from the content directory."""
        if not self.content_dir.exists():
            print(f"Error: Content directory '{self.content_dir}' does not exist")
            sys.exit(1)

        self.posts = []
        for md_file in self.content_dir.glob("*.md"):
            post = HugoPost(md_file)
            if post.has_frontmatter:
                self.posts.append(post)

        print(f"Loaded {len(self.posts)} posts from {self.content_dir}")

    def filter_posts(
        self,
        select_all: bool = False,
        title_pattern: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        text_pattern: Optional[str] = None,
        paths: Optional[List[str]] = None,
    ) -> List[HugoPost]:
        """Filter posts based on selection criteria."""

        if select_all:
            return self.posts

        # Path-based selection
        if paths:
            filtered = []
            for path_str in paths:
                # Convert to absolute path
                path = Path(path_str).resolve()

                # Find matching post
                found = False
                for post in self.posts:
                    if post.file_path.resolve() == path:
                        filtered.append(post)
                        found = True
                        break

                if not found:
                    print(f"Warning: Path not found or no frontmatter: {path_str}")

            return filtered

        filtered = []
        for post in self.posts:
            # Title filter
            if title_pattern and title_pattern.lower() not in post.get_title().lower():
                continue

            # Date filters
            post_date = post.get_date()
            if from_date and (not post_date or post_date < from_date):
                continue
            if to_date and (not post_date or post_date > to_date):
                continue

            # Text filter
            if text_pattern and text_pattern.lower() not in post.get_full_text().lower():
                continue

            filtered.append(post)

        return filtered


def parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as err:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: {date_str}. Use YYYY-MM-DD"
        ) from err


def add_post_selection_args(parser: argparse.ArgumentParser, include_text: bool = True):
    """Add common post selection arguments to an argument parser.

    Args:
        parser: The argument parser to add arguments to
        include_text: Whether to include the --text argument (default: True)
    """
    selection = parser.add_argument_group("post selection")
    selection.add_argument("--all", action="store_true", help="Select all posts")
    selection.add_argument(
        "--title", type=str, metavar="PATTERN", help="Select posts with title matching PATTERN"
    )
    selection.add_argument(
        "--fromdate",
        type=parse_date,
        metavar="YYYY-MM-DD",
        help="Select posts from this date onwards",
    )
    selection.add_argument(
        "--todate", type=parse_date, metavar="YYYY-MM-DD", help="Select posts up to this date"
    )

    if include_text:
        selection.add_argument(
            "--text",
            type=str,
            metavar="PATTERN",
            help="Select posts with PATTERN in header or content",
        )

    selection.add_argument(
        "--path",
        type=str,
        nargs="+",
        metavar="PATH",
        help="Select posts by exact/relative file paths (one or more)",
    )


def add_common_args(parser: argparse.ArgumentParser):
    """Add common arguments (dry-run, content-dir) to an argument parser."""
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without modifying files"
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=Path("content/posts"),
        help="Path to Hugo content directory (default: content/posts)",
    )


def validate_post_selection_args(args, parser: argparse.ArgumentParser, include_text: bool = True):
    """Validate that at least one post selection option is provided.

    Args:
        args: The parsed arguments
        parser: The argument parser (for error reporting)
        include_text: Whether --text was included in the available options
    """
    options = [args.all, args.title, args.fromdate, args.todate, args.path]
    if include_text:
        options.append(args.text)

    if not any(options):
        if include_text:
            parser.error(
                "At least one post selection option is required (--all, --title, --fromdate, --todate, --text, --path)"
            )
        else:
            parser.error(
                "At least one post selection option is required (--all, --title, --fromdate, --todate, --path)"
            )
