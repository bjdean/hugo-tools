#!/usr/bin/env python3
"""
Hugo Tag/Category Manager

Manages tags and categories in Hugo markdown post files.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Set, Optional

from hugotools.common import (
    HugoPost,
    HugoPostManager,
    add_post_selection_args,
    add_common_args,
    validate_post_selection_args
)


class HugoTagManager(HugoPostManager):
    """Manages tags and categories in Hugo posts."""

    def modify_metadata(self,
                       posts: List[HugoPost],
                       field: str,
                       add_items: Set[str],
                       remove_items: Set[str],
                       dry_run: bool = False):
        """Add or remove tags/categories from posts."""

        modified_count = 0

        for post in posts:
            current_items = set(post.get_metadata_list(field))
            original_items = current_items.copy()

            # Add items
            if add_items:
                current_items.update(add_items)

            # Remove items
            if remove_items:
                current_items.difference_update(remove_items)

            # Check if anything changed
            if current_items != original_items:
                modified_count += 1

                # Show what's changing
                added = current_items - original_items
                removed = original_items - current_items

                changes = []
                if added:
                    changes.append(f"+{sorted(added)}")
                if removed:
                    changes.append(f"-{sorted(removed)}")

                status = "[DRY RUN] " if dry_run else ""
                print(f"{status}Modifying {post.file_path.name}: {' '.join(changes)}")
                print(f"  {field}: {sorted(original_items)} -> {sorted(current_items)}")

                # Save if not dry run
                if not dry_run:
                    post.set_metadata_list(field, sorted(current_items))
                    post.save()

        return modified_count

    def modify_label(self,
                    posts: List[HugoPost],
                    field: str,
                    set_value: Optional[str],
                    remove: bool = False,
                    dry_run: bool = False):
        """Set or remove a single-value label field in posts."""

        modified_count = 0

        for post in posts:
            current_value = post.get_metadata_label(field)

            # Determine the new value
            if remove:
                new_value = None
            elif set_value is not None:
                new_value = set_value
            else:
                continue  # Nothing to do

            # Check if anything changed
            if current_value != new_value:
                modified_count += 1

                # Show what's changing
                status = "[DRY RUN] " if dry_run else ""
                print(f"{status}Modifying {post.file_path.name}")
                if new_value is None:
                    print(f"  {field}: '{current_value}' -> (removed)")
                else:
                    print(f"  {field}: '{current_value}' -> '{new_value}'")

                # Save if not dry run
                if not dry_run:
                    post.set_metadata_label(field, new_value)
                    post.save()

        return modified_count

    def dump_metadata(self, posts: List[HugoPost], field: str, field_type: str):
        """Dump metadata field values from posts."""

        print(f"{'='*60}")
        print(f"Dumping '{field}' from {len(posts)} posts")
        print(f"{'='*60}\n")

        if field_type == 'list':
            # For list fields, show all items
            all_values = set()
            for post in posts:
                items = post.get_metadata_list(field)
                if items:
                    print(f"{post.file_path.name}:")
                    print(f"  {field}: {items}")
                    all_values.update(items)
                else:
                    print(f"{post.file_path.name}:")
                    print(f"  {field}: (not found or empty)")

            print(f"\n{'='*60}")
            print(f"Summary: {len(all_values)} unique values")
            if all_values:
                print(f"All values: {sorted(all_values)}")
            print(f"{'='*60}")

        else:  # label field
            # For label fields, show single value
            all_values = set()
            for post in posts:
                value = post.get_metadata_label(field)
                if value is not None:
                    print(f"{post.file_path.name}:")
                    print(f"  {field}: '{value}'")
                    all_values.add(value)
                else:
                    print(f"{post.file_path.name}:")
                    print(f"  {field}: (not found)")

            print(f"\n{'='*60}")
            print(f"Summary: {len(all_values)} unique values")
            if all_values:
                print(f"All values: {sorted(all_values)}")
            print(f"{'='*60}")


def run(args=None):
    """Run the tag manager command."""
    parser = argparse.ArgumentParser(
        prog='hugotools tag',
        description='Manage tags and categories in Hugo posts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add 'python' tag to all posts
  hugotools tag --all --add python

  # Remove 'draft' tag from posts with 'docker' in title
  hugotools tag --title docker --remove draft

  # Add multiple tags to posts from 2023
  hugotools tag --fromdate 2023-01-01 --add "ai,machine-learning"

  # Modify categories instead of tags
  hugotools tag --all --categories --add "Tech"

  # Set a custom label field
  hugotools tag --title "My Post" --custom-label status --set "published"

  # Add items to a custom list field
  hugotools tag --all --custom-list keywords --add "tutorial,beginner"

  # Remove a custom label field entirely
  hugotools tag --text "old post" --custom-label draft --remove true

  # Dump all tags from all posts
  hugotools tag --all --dump

  # Dump categories from posts with 'docker' in title
  hugotools tag --title docker --categories --dump

  # Dump custom field values
  hugotools tag --all --custom-label author --dump

  # Update specific posts by path
  hugotools tag --path content/posts/2023-01-01-mypost.md --add "tutorial"

  # Update multiple posts by path
  hugotools tag --path content/posts/post1.md content/posts/post2.md --add "updated"

  # Dry run to see what would change
  hugotools tag --all --add test --dry-run
        """
    )

    # Field selection
    field_group = parser.add_argument_group('field selection (choose one)')
    field_group.add_argument('--categories', action='store_true',
                        help='Operate on categories instead of tags (default: tags)')
    field_group.add_argument('--custom-list', type=str, metavar='FIELDNAME',
                        help='Operate on a custom list field (e.g., keywords, authors)')
    field_group.add_argument('--custom-label', type=str, metavar='FIELDNAME',
                        help='Operate on a custom single-value field (e.g., status, series)')

    # Post selection (using common function)
    add_post_selection_args(parser, include_text=True)

    # Operations
    operations = parser.add_argument_group('operations')
    operations.add_argument('--add', type=str, metavar='TAG[,TAG...]',
                           help='Add items to list fields (comma-separated)')
    operations.add_argument('--remove', type=str, metavar='TAG[,TAG...]',
                           help='Remove items from list fields OR remove a label field entirely (comma-separated for lists)')
    operations.add_argument('--set', type=str, metavar='VALUE',
                           help='Set value for label fields (use with --custom-label)')
    operations.add_argument('--dump', action='store_true',
                           help='Report current values of the selected field without modifying')

    # Common options (using common function)
    add_common_args(parser)

    parsed_args = parser.parse_args(args)

    # Validate post selection arguments (using common function)
    validate_post_selection_args(parsed_args, parser, include_text=True)

    # Determine field name and type
    field_options = [parsed_args.categories, parsed_args.custom_list, parsed_args.custom_label]
    if sum(bool(x) for x in field_options) > 1:
        parser.error("Only one of --categories, --custom-list, or --custom-label can be specified")

    is_label_field = bool(parsed_args.custom_label)

    if parsed_args.custom_label:
        field = parsed_args.custom_label
        field_type = 'label'
    elif parsed_args.custom_list:
        field = parsed_args.custom_list
        field_type = 'list'
    elif parsed_args.categories:
        field = 'categories'
        field_type = 'list'
    else:
        field = 'tags'
        field_type = 'list'

    # Validate operations based on field type
    if parsed_args.dump:
        # In dump mode, we don't need other operations
        if any([parsed_args.add, parsed_args.remove, parsed_args.set]):
            parser.error("Cannot use --dump with --add, --remove, or --set")
    else:
        # Not in dump mode, require modification operations
        if field_type == 'label':
            # For labels, we need either --set or --remove
            if not any([parsed_args.set, parsed_args.remove]):
                parser.error("For label fields, at least one operation is required (--set or --remove)")
            if parsed_args.add:
                parser.error("Cannot use --add with label fields. Use --set instead.")
        else:
            # For lists, we need --add or --remove (but not --set)
            if not any([parsed_args.add, parsed_args.remove]):
                parser.error("At least one operation is required (--add or --remove)")
            if parsed_args.set:
                parser.error("Cannot use --set with list fields. Use --add instead.")

    print(f"{'='*60}")
    print(f"Hugo {field.capitalize()} Manager")
    print(f"{'='*60}")
    if parsed_args.dry_run:
        print("[DRY RUN MODE - No files will be modified]")
    print()

    # Load and filter posts
    manager = HugoTagManager(parsed_args.content_dir)
    manager.load_posts()

    selected_posts = manager.filter_posts(
        select_all=parsed_args.all,
        title_pattern=parsed_args.title,
        from_date=parsed_args.fromdate,
        to_date=parsed_args.todate,
        text_pattern=getattr(parsed_args, 'text', None),
        paths=parsed_args.path
    )

    print(f"Selected {len(selected_posts)} posts")
    print()

    if not selected_posts:
        print("No posts selected. Exiting.")
        return 0

    # Handle dump mode
    if parsed_args.dump:
        manager.dump_metadata(selected_posts, field, field_type)
        return 0

    # Modify posts based on field type
    if field_type == 'label':
        # Handle label (single-value) fields
        if parsed_args.set:
            print(f"Setting {field}: '{parsed_args.set}'")
        if parsed_args.remove:
            print(f"Removing {field}")
        print()

        modified_count = manager.modify_label(
            selected_posts,
            field,
            set_value=parsed_args.set,
            remove=bool(parsed_args.remove),
            dry_run=parsed_args.dry_run
        )
    else:
        # Handle list fields
        add_items = set(parsed_args.add.split(',')) if parsed_args.add else set()
        remove_items = set(parsed_args.remove.split(',')) if parsed_args.remove else set()

        # Strip whitespace
        add_items = {item.strip() for item in add_items}
        remove_items = {item.strip() for item in remove_items}

        if add_items:
            print(f"Adding {field}: {sorted(add_items)}")
        if remove_items:
            print(f"Removing {field}: {sorted(remove_items)}")
        print()

        modified_count = manager.modify_metadata(
            selected_posts,
            field,
            add_items,
            remove_items,
            dry_run=parsed_args.dry_run
        )

    print()
    print(f"{'='*60}")
    if parsed_args.dry_run:
        print(f"[DRY RUN] Would modify {modified_count} of {len(selected_posts)} posts")
    else:
        print(f"Modified {modified_count} of {len(selected_posts)} posts")
    print(f"{'='*60}")

    return 0


if __name__ == '__main__':
    sys.exit(run())
