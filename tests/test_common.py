"""Tests for common Hugo post handling utilities."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from hugotools.common import HugoPost, HugoPostManager


def test_hugo_post_parsing():
    """Test parsing a Hugo post with frontmatter."""
    content = """---
title: Test Post
date: 2023-01-15 10:30:00
tags:
  - python
  - testing
categories:
  - Technology
---

This is the post content.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)

        assert post.has_frontmatter
        assert post.get_title() == "Test Post"
        assert post.get_metadata_list("tags") == ["python", "testing"]
        assert post.get_metadata_list("categories") == ["Technology"]
        assert "This is the post content." in post.content

        # Test date parsing
        post_date = post.get_date()
        assert post_date is not None
        assert post_date.year == 2023
        assert post_date.month == 1
        assert post_date.day == 15

    finally:
        temp_path.unlink()


def test_hugo_post_no_frontmatter():
    """Test handling posts without frontmatter."""
    content = "Just plain markdown content."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)

        assert not post.has_frontmatter
        assert post.content == content
        assert post.frontmatter == {}

    finally:
        temp_path.unlink()


def test_hugo_post_metadata_modification():
    """Test adding and removing metadata."""
    content = """---
title: Test Post
tags:
  - original
---

Content here.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)

        # Add tags
        tags = post.get_metadata_list("tags")
        tags.append("new-tag")
        post.set_metadata_list("tags", tags)
        post.save()

        # Re-read and verify
        post2 = HugoPost(temp_path)
        assert "original" in post2.get_metadata_list("tags")
        assert "new-tag" in post2.get_metadata_list("tags")

    finally:
        temp_path.unlink()


def test_hugo_post_manager_loading():
    """Test loading multiple posts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        # Create test posts
        for i in range(3):
            post_file = content_dir / f"post{i}.md"
            post_file.write_text(
                f"""---
title: Post {i}
date: 2023-01-{i+1:02d}
---

Content {i}
"""
            )

        # Create a non-markdown file (should be ignored)
        (content_dir / "readme.txt").write_text("Not a post")

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        assert len(manager.posts) == 3
        titles = [post.get_title() for post in manager.posts]
        assert "Post 0" in titles
        assert "Post 1" in titles
        assert "Post 2" in titles


def test_hugo_post_manager_filtering_by_title():
    """Test filtering posts by title pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        (content_dir / "python-post.md").write_text(
            """---
title: Python Tutorial
---
Content
"""
        )
        (content_dir / "javascript-post.md").write_text(
            """---
title: JavaScript Guide
---
Content
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Filter by title
        filtered = manager.filter_posts(title_pattern="python")
        assert len(filtered) == 1
        assert filtered[0].get_title() == "Python Tutorial"


def test_hugo_post_manager_filtering_by_date():
    """Test filtering posts by date range."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        (content_dir / "old-post.md").write_text(
            """---
title: Old Post
date: 2020-01-01
---
Content
"""
        )
        (content_dir / "new-post.md").write_text(
            """---
title: New Post
date: 2023-01-01
---
Content
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Filter by date
        from_date = datetime(2022, 1, 1)
        filtered = manager.filter_posts(from_date=from_date)
        assert len(filtered) == 1
        assert filtered[0].get_title() == "New Post"


def test_hugo_post_toml_parsing():
    """Test parsing a Hugo post with TOML frontmatter."""
    content = """+++
title = "Test TOML Post"
date = 2023-01-15T10:30:00Z
tags = ["python", "testing"]
categories = ["Technology"]
+++

This is the post content with TOML frontmatter.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)

        assert post.has_frontmatter
        assert post.frontmatter_format == "toml"
        assert post.get_title() == "Test TOML Post"
        assert post.get_metadata_list("tags") == ["python", "testing"]
        assert post.get_metadata_list("categories") == ["Technology"]
        assert "This is the post content with TOML frontmatter." in post.content

    finally:
        temp_path.unlink()


def test_hugo_post_json_parsing():
    """Test parsing a Hugo post with JSON frontmatter."""
    content = """{
  "title": "Test JSON Post",
  "date": "2023-01-15T10:30:00Z",
  "tags": ["python", "testing"],
  "categories": ["Technology"]
}

This is the post content with JSON frontmatter.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)

        assert post.has_frontmatter
        assert post.frontmatter_format == "json"
        assert post.get_title() == "Test JSON Post"
        assert post.get_metadata_list("tags") == ["python", "testing"]
        assert post.get_metadata_list("categories") == ["Technology"]
        assert "This is the post content with JSON frontmatter." in post.content

    finally:
        temp_path.unlink()


def test_hugo_post_toml_save_preserves_format():
    """Test that saving a TOML post preserves the TOML format."""
    content = """+++
title = "Test TOML Post"
tags = ["original"]
+++

Content here.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)

        # Modify tags
        tags = post.get_metadata_list("tags")
        tags.append("new-tag")
        post.set_metadata_list("tags", tags)
        post.save()

        # Re-read and verify format is preserved
        saved_content = temp_path.read_text()
        assert saved_content.startswith("+++")
        assert "+++" in saved_content[3:]  # Check closing delimiter

        # Verify content is correct
        post2 = HugoPost(temp_path)
        assert post2.frontmatter_format == "toml"
        assert "original" in post2.get_metadata_list("tags")
        assert "new-tag" in post2.get_metadata_list("tags")

    finally:
        temp_path.unlink()


def test_hugo_post_json_save_preserves_format():
    """Test that saving a JSON post preserves the JSON format."""
    content = """{
  "title": "Test JSON Post",
  "tags": ["original"]
}

Content here.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)

        # Modify tags
        tags = post.get_metadata_list("tags")
        tags.append("new-tag")
        post.set_metadata_list("tags", tags)
        post.save()

        # Re-read and verify format is preserved
        saved_content = temp_path.read_text()
        assert saved_content.startswith("{")

        # Verify content is correct
        post2 = HugoPost(temp_path)
        assert post2.frontmatter_format == "json"
        assert "original" in post2.get_metadata_list("tags")
        assert "new-tag" in post2.get_metadata_list("tags")

    finally:
        temp_path.unlink()


def test_hugo_post_manager_loading_mixed_formats():
    """Test loading posts with different frontmatter formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        # Create YAML post
        (content_dir / "yaml-post.md").write_text(
            """---
title: YAML Post
date: 2023-01-01
---
Content
"""
        )

        # Create TOML post
        (content_dir / "toml-post.md").write_text(
            """+++
title = "TOML Post"
date = 2023-01-02
+++
Content
"""
        )

        # Create JSON post
        (content_dir / "json-post.md").write_text(
            """{
  "title": "JSON Post",
  "date": "2023-01-03"
}
Content
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Should load all three posts regardless of format
        assert len(manager.posts) == 3
        titles = [post.get_title() for post in manager.posts]
        assert "YAML Post" in titles
        assert "TOML Post" in titles
        assert "JSON Post" in titles


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
