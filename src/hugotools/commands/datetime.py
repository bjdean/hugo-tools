#!/usr/bin/env python3
"""
Hugo Post Datetime Synchronizer

Updates post file modification times to match their frontmatter date metadata.
Only modifies files when the datetime differs from the metadata.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List

from hugotools.common import (
    HugoPost,
    HugoPostManager,
    add_post_selection_args,
    add_common_args,
    validate_post_selection_args
)


class DatetimeSynchronizer(HugoPostManager):
    """Synchronizes file modification times with frontmatter dates."""

    def synchronize_datetimes(self, posts: List[HugoPost], dry_run: bool = False) -> int:
        """Update file modification times to match frontmatter dates."""
        modified_count = 0
        skipped_count = 0
        error_count = 0

        for post in posts:
            # Get the date from frontmatter
            post_date = post.get_date()

            if not post_date:
                print(f"[SKIP] {post.file_path.name}: No valid date in frontmatter")
                skipped_count += 1
                continue

            # Get current file modification time
            file_stat = post.file_path.stat()
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

            # Compare dates (ignore microseconds)
            post_date_truncated = post_date.replace(microsecond=0)
            file_mtime_truncated = file_mtime.replace(microsecond=0)

            if post_date_truncated == file_mtime_truncated:
                # Already synchronized
                continue

            modified_count += 1
            status = "[DRY RUN] " if dry_run else ""

            print(f"{status}{post.file_path.name}:")
            print(f"  Frontmatter date: {post_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  File mtime:       {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  → Setting file mtime to match frontmatter date")

            # Update file modification time if not dry run
            if not dry_run:
                try:
                    # Convert datetime to timestamp
                    timestamp = post_date.timestamp()

                    # Update both access time and modification time
                    os.utime(post.file_path, (timestamp, timestamp))

                except Exception as e:
                    print(f"  ERROR: Failed to update file time: {e}")
                    error_count += 1
                    modified_count -= 1

        return modified_count, skipped_count, error_count


def run(args=None):
    """Run the datetime synchronizer command."""
    parser = argparse.ArgumentParser(
        prog='hugotools datetime',
        description='Synchronize Hugo post file modification times with frontmatter dates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync all posts
  hugotools datetime --all

  # Sync specific posts by path
  hugotools datetime --path content/posts/2023-01-01-mypost.md

  # Sync multiple posts
  hugotools datetime --path content/posts/post1.md content/posts/post2.md

  # Sync posts with 'docker' in title
  hugotools datetime --title docker

  # Sync posts from 2023
  hugotools datetime --fromdate 2023-01-01 --todate 2023-12-31

  # Dry run to see what would change
  hugotools datetime --all --dry-run
        """
    )

    # Post selection (using common function, without --text since it's not useful for datetime sync)
    add_post_selection_args(parser, include_text=False)

    # Common options (using common function)
    add_common_args(parser)

    parsed_args = parser.parse_args(args)

    # Validate post selection arguments (using common function)
    validate_post_selection_args(parsed_args, parser, include_text=False)

    print(f"{'='*60}")
    print(f"Hugo Post Datetime Synchronizer")
    print(f"{'='*60}")
    if parsed_args.dry_run:
        print("[DRY RUN MODE - No files will be modified]")
    print()

    # Load and filter posts
    synchronizer = DatetimeSynchronizer(parsed_args.content_dir)
    synchronizer.load_posts()

    selected_posts = synchronizer.filter_posts(
        select_all=parsed_args.all,
        title_pattern=parsed_args.title,
        from_date=parsed_args.fromdate,
        to_date=parsed_args.todate,
        paths=parsed_args.path
    )

    print(f"Selected {len(selected_posts)} posts")
    print()

    if not selected_posts:
        print("No posts selected. Exiting.")
        return 0

    # Synchronize datetimes
    modified_count, skipped_count, error_count = synchronizer.synchronize_datetimes(
        selected_posts,
        dry_run=parsed_args.dry_run
    )

    print()
    print(f"{'='*60}")
    if parsed_args.dry_run:
        print(f"[DRY RUN] Would update {modified_count} of {len(selected_posts)} posts")
    else:
        print(f"Updated {modified_count} of {len(selected_posts)} posts")

    if skipped_count > 0:
        print(f"Skipped {skipped_count} posts (no valid date in frontmatter)")

    if error_count > 0:
        print(f"Errors: {error_count} posts failed to update")

    print(f"{'='*60}")

    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(run())
