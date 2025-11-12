"""Tests for CLI entry point and command routing."""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from hugotools.cli import main


def test_cli_no_command_shows_help():
    """Test that running CLI without command shows help."""
    with patch("sys.argv", ["hugotools"]):
        result = main()
        assert result == 0


def test_cli_version_flag():
    """Test that --version flag works."""
    with patch("sys.argv", ["hugotools", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_cli_datetime_command_routing(tmp_path):
    """Test that datetime command routes correctly."""
    # Create a temporary content directory
    content_dir = tmp_path / "content" / "posts"
    content_dir.mkdir(parents=True)

    # Create a sample post
    post_file = content_dir / "test.md"
    post_file.write_text("""---
title: Test Post
date: 2023-01-15 10:30:00
---

Content here.
""")

    with patch("sys.argv", ["hugotools", "datetime", "--all", "--content-dir", str(content_dir), "--dry-run"]):
        result = main()
        assert result == 0


def test_cli_tag_command_routing(tmp_path):
    """Test that tag command routes correctly."""
    # Create a temporary content directory
    content_dir = tmp_path / "content" / "posts"
    content_dir.mkdir(parents=True)

    # Create a sample post
    post_file = content_dir / "test.md"
    post_file.write_text("""---
title: Test Post
tags:
  - python
---

Content here.
""")

    with patch("sys.argv", ["hugotools", "tag", "--all", "--add", "test", "--content-dir", str(content_dir), "--dry-run"]):
        result = main()
        assert result == 0


def test_cli_import_command_routing(tmp_path):
    """Test that import command routes correctly."""
    # Create a minimal WordPress XML export
    xml_file = tmp_path / "export.xml"
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
    <item>
        <title>Test Post</title>
        <link>http://example.com/2023/01/test-post/</link>
        <pubDate>Mon, 15 Jan 2023 10:30:00 +0000</pubDate>
        <dc:creator><![CDATA[admin]]></dc:creator>
        <content:encoded><![CDATA[<p>Test content</p>]]></content:encoded>
        <wp:post_id>1</wp:post_id>
        <wp:post_date>2023-01-15 10:30:00</wp:post_date>
        <wp:post_name>test-post</wp:post_name>
        <wp:status>publish</wp:status>
        <wp:post_type>post</wp:post_type>
    </item>
</channel>
</rss>
"""
    xml_file.write_text(xml_content)

    output_dir = tmp_path / "output"

    with patch("sys.argv", ["hugotools", "import", str(xml_file), "--output-dir", str(output_dir), "--dry-run"]):
        result = main()
        assert result == 0


def test_cli_help_flag():
    """Test that --help flag works."""
    with patch("sys.argv", ["hugotools", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_cli_datetime_help():
    """Test that datetime --help works."""
    with patch("sys.argv", ["hugotools", "datetime", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_cli_tag_help():
    """Test that tag --help works."""
    with patch("sys.argv", ["hugotools", "tag", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_cli_import_help():
    """Test that import --help works."""
    with patch("sys.argv", ["hugotools", "import", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
