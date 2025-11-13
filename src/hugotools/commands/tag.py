#!/usr/bin/env python3
"""
Hugo Tag/Category Manager

Manages tags and categories in Hugo markdown post files.
"""

import argparse
import sys
from typing import List, Optional, Set

from hugotools.common import (
    HugoPost,
    HugoPostManager,
    add_common_args,
    add_post_selection_args,
    validate_post_selection_args,
)


class HugoTagManager(HugoPostManager):
    """Manages tags and categories in Hugo posts."""

    def modify_metadata(
        self,
        posts: List[HugoPost],
        field: str,
        add_items: Set[str],
        remove_items: Set[str],
        dry_run: bool = False,
    ):
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

    def modify_label(
        self,
        posts: List[HugoPost],
        field: str,
        set_value: Optional[str],
        remove: bool = False,
        dry_run: bool = False,
    ):
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

        if field_type == "list":
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

    def copy_or_move_metadata(
        self,
        posts: List[HugoPost],
        source_field: str,
        source_type: str,
        dest_field: str,
        dest_type: str,
        move: bool = False,
        dry_run: bool = False,
    ):
        """Copy or move metadata from one field to another.

        Args:
            posts: List of posts to modify
            source_field: Source field name
            source_type: Source field type ('list' or 'label')
            dest_field: Destination field name
            dest_type: Destination field type ('list' or 'label')
            move: If True, remove from source after copying; if False, just copy
            dry_run: If True, don't actually modify files

        Raises:
            ValueError: If source_type and dest_type don't match
        """

        # Validate field types match
        if source_type != dest_type:
            raise ValueError(
                f"Cannot copy/move between different field types: "
                f"{source_field} ({source_type}) -> {dest_field} ({dest_type}). "
                f"List fields can only be copied/moved to other list fields, "
                f"and label fields can only be copied/moved to other label fields."
            )

        modified_count = 0

        for post in posts:
            if source_type == "list":
                # Handle list fields
                source_items = set(post.get_metadata_list(source_field))
                dest_items = set(post.get_metadata_list(dest_field))

                if not source_items:
                    continue  # Nothing to copy/move

                original_dest = dest_items.copy()
                original_source = source_items.copy()

                # Copy items to destination
                dest_items.update(source_items)

                # If moving, clear source
                if move:
                    source_items.clear()

                # Check if anything changed
                dest_changed = dest_items != original_dest
                source_changed = source_items != original_source

                if dest_changed or source_changed:
                    modified_count += 1

                    # Show what's changing
                    status = "[DRY RUN] " if dry_run else ""
                    operation = "Moving" if move else "Copying"
                    print(f"{status}{operation} in {post.file_path.name}")
                    print(f"  {source_field}: {sorted(original_source)} -> {sorted(source_items)}")
                    print(f"  {dest_field}: {sorted(original_dest)} -> {sorted(dest_items)}")

                    # Save if not dry run
                    if not dry_run:
                        post.set_metadata_list(dest_field, sorted(dest_items))
                        if move:
                            if source_items:
                                post.set_metadata_list(source_field, sorted(source_items))
                            else:
                                # Remove the field entirely if empty after move
                                post.set_metadata_list(source_field, [])
                        post.save()

            else:  # label field
                # Handle label fields
                source_value = post.get_metadata_label(source_field)
                dest_value = post.get_metadata_label(dest_field)

                if source_value is None:
                    continue  # Nothing to copy/move

                # Copy value to destination
                new_dest_value = source_value
                new_source_value = None if move else source_value

                # Check if anything changed
                dest_changed = new_dest_value != dest_value
                source_changed = new_source_value != source_value

                if dest_changed or source_changed:
                    modified_count += 1

                    # Show what's changing
                    status = "[DRY RUN] " if dry_run else ""
                    operation = "Moving" if move else "Copying"
                    print(f"{status}{operation} in {post.file_path.name}")
                    if move:
                        print(f"  {source_field}: '{source_value}' -> (removed)")
                    else:
                        print(f"  {source_field}: '{source_value}' (unchanged)")
                    print(f"  {dest_field}: '{dest_value}' -> '{new_dest_value}'")

                    # Save if not dry run
                    if not dry_run:
                        post.set_metadata_label(dest_field, new_dest_value)
                        if move:
                            post.set_metadata_label(source_field, None)
                        post.save()

        return modified_count


def run(args=None):
    """Run the tag manager command."""
    parser = argparse.ArgumentParser(
        prog="hugotools tag",
        description="Manage tags and categories in Hugo posts",
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

  # Copy all categories to tags
  hugotools tag --all --copy categories

  # Move all tags to categories
  hugotools tag --all --move tags --categories

  # Copy custom list field to another
  hugotools tag --all --copy keywords --custom-list topics

  # Move label field to another label field
  hugotools tag --all --move author --custom-label editor
        """,
    )

    # Field selection
    field_group = parser.add_argument_group("field selection (choose one)")
    field_group.add_argument(
        "--categories",
        action="store_true",
        help="Operate on categories instead of tags (default: tags)",
    )
    field_group.add_argument(
        "--custom-list",
        type=str,
        metavar="FIELDNAME",
        help="Operate on a custom list field (e.g., keywords, authors)",
    )
    field_group.add_argument(
        "--custom-label",
        type=str,
        metavar="FIELDNAME",
        help="Operate on a custom single-value field (e.g., status, series)",
    )

    # Post selection (using common function)
    add_post_selection_args(parser, include_text=True)

    # Operations
    operations = parser.add_argument_group("operations")
    operations.add_argument(
        "--add", type=str, metavar="TAG[,TAG...]", help="Add items to list fields (comma-separated)"
    )
    operations.add_argument(
        "--remove",
        type=str,
        metavar="TAG[,TAG...]",
        help="Remove items from list fields OR remove a label field entirely (comma-separated for lists)",
    )
    operations.add_argument(
        "--set",
        type=str,
        metavar="VALUE",
        help="Set value for label fields (use with --custom-label)",
    )
    operations.add_argument(
        "--copy",
        type=str,
        metavar="SOURCEFIELD",
        help="Copy values from SOURCEFIELD to the destination field (selected by --categories, --custom-list, or --custom-label). "
        "Both fields must be the same type (both lists or both labels).",
    )
    operations.add_argument(
        "--move",
        type=str,
        metavar="SOURCEFIELD",
        help="Move values from SOURCEFIELD to the destination field (selected by --categories, --custom-list, or --custom-label). "
        "Both fields must be the same type (both lists or both labels). Source field will be cleared after move.",
    )
    operations.add_argument(
        "--dump",
        action="store_true",
        help="Report current values of the selected field without modifying",
    )

    # Common options (using common function)
    add_common_args(parser)

    parsed_args = parser.parse_args(args)

    # Validate post selection arguments (using common function)
    validate_post_selection_args(parsed_args, parser, include_text=True)

    # Determine field name and type
    field_options = [parsed_args.categories, parsed_args.custom_list, parsed_args.custom_label]
    if sum(bool(x) for x in field_options) > 1:
        parser.error("Only one of --categories, --custom-list, or --custom-label can be specified")

    if parsed_args.custom_label:
        field = parsed_args.custom_label
        field_type = "label"
    elif parsed_args.custom_list:
        field = parsed_args.custom_list
        field_type = "list"
    elif parsed_args.categories:
        field = "categories"
        field_type = "list"
    else:
        field = "tags"
        field_type = "list"

    # Validate operations based on field type
    if parsed_args.dump:
        # In dump mode, we don't need other operations
        if any(
            [
                parsed_args.add,
                parsed_args.remove,
                parsed_args.set,
                parsed_args.copy,
                parsed_args.move,
            ]
        ):
            parser.error("Cannot use --dump with --add, --remove, --set, --copy, or --move")
    elif parsed_args.copy or parsed_args.move:
        # Copy/move mode - validate
        if parsed_args.copy and parsed_args.move:
            parser.error("Cannot use both --copy and --move at the same time")
        if any([parsed_args.add, parsed_args.remove, parsed_args.set]):
            parser.error("Cannot use --copy or --move with --add, --remove, or --set")
    else:
        # Not in dump or copy/move mode, require modification operations
        if field_type == "label":
            # For labels, we need either --set or --remove
            if not any([parsed_args.set, parsed_args.remove]):
                parser.error(
                    "For label fields, at least one operation is required (--set or --remove)"
                )
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
        text_pattern=getattr(parsed_args, "text", None),
        paths=parsed_args.path,
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

    # Handle copy/move mode
    if parsed_args.copy or parsed_args.move:
        source_field = parsed_args.copy if parsed_args.copy else parsed_args.move
        dest_field = field
        is_move = bool(parsed_args.move)

        # Determine source field type
        # We need to infer the type based on common Hugo fields
        # or assume it's the same type as the destination
        known_list_fields = ["tags", "categories", "keywords", "authors", "series"]
        known_label_fields = ["author", "title", "date", "draft", "status"]

        if source_field in known_list_fields:
            source_type = "list"
        elif source_field in known_label_fields:
            source_type = "label"
        else:
            # Assume same type as destination for custom fields
            source_type = field_type

        operation = "Moving" if is_move else "Copying"
        print(f"{operation} from {source_field} ({source_type}) to {dest_field} ({field_type})")
        print()

        try:
            modified_count = manager.copy_or_move_metadata(
                selected_posts,
                source_field=source_field,
                source_type=source_type,
                dest_field=dest_field,
                dest_type=field_type,
                move=is_move,
                dry_run=parsed_args.dry_run,
            )
        except ValueError as e:
            parser.error(str(e))

    # Modify posts based on field type
    elif field_type == "label":
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
            dry_run=parsed_args.dry_run,
        )
    else:
        # Handle list fields
        add_items = set(parsed_args.add.split(",")) if parsed_args.add else set()
        remove_items = set(parsed_args.remove.split(",")) if parsed_args.remove else set()

        # Strip whitespace
        add_items = {item.strip() for item in add_items}
        remove_items = {item.strip() for item in remove_items}

        if add_items:
            print(f"Adding {field}: {sorted(add_items)}")
        if remove_items:
            print(f"Removing {field}: {sorted(remove_items)}")
        print()

        modified_count = manager.modify_metadata(
            selected_posts, field, add_items, remove_items, dry_run=parsed_args.dry_run
        )

    print()
    print(f"{'='*60}")
    if parsed_args.dry_run:
        print(f"[DRY RUN] Would modify {modified_count} of {len(selected_posts)} posts")
    else:
        print(f"Modified {modified_count} of {len(selected_posts)} posts")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(run())
