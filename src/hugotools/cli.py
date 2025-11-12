#!/usr/bin/env python3
"""
Hugo Tools CLI - Main command router with subcommands.

Provides a unified command-line interface for Hugo site management tools.
"""

import argparse
import sys

from hugotools.version import __version__


def main():
    """Main CLI entry point with subcommand routing."""
    parser = argparse.ArgumentParser(
        prog="hugotools",
        description="A toolkit for managing Hugo sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  datetime    Synchronize file modification times with frontmatter dates
  tag         Manage tags, categories, and other metadata fields
  import      Import content from external sources (WordPress, etc.)

Examples:
  # Sync all post file dates with their frontmatter
  hugotools datetime --all

  # Add tags to posts
  hugotools tag --all --add "python,tutorial"

  # Import WordPress export
  hugotools import wordpress-export.xml --output-dir content/posts

For help on a specific command:
  hugotools <command> --help
        """,
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command", title="commands", description="Available commands", help="Command to run"
    )

    # Import command modules (lazy import to speed up CLI startup)
    # We'll set up subparsers here and import modules only when needed

    # datetime command
    subparsers.add_parser(
        "datetime",
        help="Synchronize file modification times with frontmatter dates",
        add_help=False,  # We'll let the command module handle its own help
    )

    # tag command
    subparsers.add_parser("tag", help="Manage tags, categories, and other metadata", add_help=False)

    # import command
    subparsers.add_parser("import", help="Import content from external sources", add_help=False)

    # Parse only the command name first
    args, remaining = parser.parse_known_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate command module
    if args.command == "datetime":
        from hugotools.commands.datetime import run

        return run(remaining)

    elif args.command == "tag":
        from hugotools.commands.tag import run

        return run(remaining)

    elif args.command == "import":
        from hugotools.commands.import_wordpress import run

        return run(remaining)

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
