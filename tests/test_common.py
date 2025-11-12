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


def test_hugo_post_yaml_parse_error():
    """Test handling of invalid YAML frontmatter."""
    content = """---
title: Test Post
date: [invalid yaml structure
---

Content here.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        # Should not crash, just have empty frontmatter
        post = HugoPost(temp_path)
        assert post.has_frontmatter
        assert post.frontmatter == {}
    finally:
        temp_path.unlink()


def test_hugo_post_toml_parse_error():
    """Test handling of invalid TOML frontmatter."""
    content = """+++
title = "Test Post"
date = [invalid toml structure
+++

Content here.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        # Should not crash, just have empty frontmatter
        post = HugoPost(temp_path)
        assert post.has_frontmatter
        assert post.frontmatter == {}
    finally:
        temp_path.unlink()


def test_hugo_post_json_parse_error():
    """Test handling of invalid JSON frontmatter."""
    content = """{
  "title": "Test Post",
  "date": "2023-01-15",
  "invalid": missing quotes and comma
}

Content here.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        # Should not crash, just have empty frontmatter
        post = HugoPost(temp_path)
        assert post.has_frontmatter
        assert post.frontmatter_format == "json"
        assert post.frontmatter == {}
    finally:
        temp_path.unlink()


def test_hugo_post_filter_by_path():
    """Test filtering posts by exact path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post1 = content_dir / "post1.md"
        post1.write_text(
            """---
title: Post 1
---
Content
"""
        )
        post2 = content_dir / "post2.md"
        post2.write_text(
            """---
title: Post 2
---
Content
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Filter by path
        filtered = manager.filter_posts(paths=[str(post1)])
        assert len(filtered) == 1
        assert filtered[0].get_title() == "Post 1"


def test_hugo_post_filter_path_not_found():
    """Test filtering with non-existent path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post1 = content_dir / "post1.md"
        post1.write_text(
            """---
title: Post 1
---
Content
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Filter by non-existent path
        filtered = manager.filter_posts(paths=["/nonexistent/path.md"])
        assert len(filtered) == 0


def test_hugo_post_get_date_various_formats():
    """Test parsing various date formats."""
    # ISO format with timezone
    content = """---
title: Test Post
date: 2023-01-15T10:30:00+00:00
---
Content
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        date = post.get_date()
        assert date is not None
        assert date.year == 2023
        assert date.month == 1
        assert date.day == 15
    finally:
        temp_path.unlink()


def test_hugo_post_get_date_invalid():
    """Test handling of invalid date format."""
    content = """---
title: Test Post
date: not-a-date
---
Content
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        date = post.get_date()
        assert date is None
    finally:
        temp_path.unlink()


def test_hugo_post_metadata_list_single_value():
    """Test get_metadata_list with a single string value."""
    content = """---
title: Test Post
category: Single
---
Content
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        # get_metadata_list should convert single value to list
        categories = post.get_metadata_list("category")
        assert categories == ["Single"]
    finally:
        temp_path.unlink()


def test_hugo_post_metadata_list_empty():
    """Test get_metadata_list with missing field."""
    content = """---
title: Test Post
---
Content
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        tags = post.get_metadata_list("tags")
        assert tags == []
    finally:
        temp_path.unlink()


def test_hugo_post_set_metadata_list_empty():
    """Test setting metadata list to empty removes the field."""
    content = """---
title: Test Post
tags:
  - python
  - tutorial
---
Content
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        post.set_metadata_list("tags", [])
        post.save()

        # Re-read and verify field is removed
        post2 = HugoPost(temp_path)
        assert "tags" not in post2.frontmatter
    finally:
        temp_path.unlink()


def test_parse_date_invalid_format():
    """Test parse_date with invalid format."""
    from hugotools.common import parse_date

    with pytest.raises(Exception):  # ArgumentTypeError
        parse_date("2023/01/01")


def test_hugo_post_filter_combined():
    """Test filtering with multiple criteria."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        (content_dir / "post1.md").write_text(
            """---
title: Python Tutorial 2023
date: 2023-06-15
---
Learn Python programming.
"""
        )
        (content_dir / "post2.md").write_text(
            """---
title: JavaScript Guide 2023
date: 2023-06-20
---
Learn JavaScript.
"""
        )
        (content_dir / "post3.md").write_text(
            """---
title: Python Advanced
date: 2020-01-01
---
Advanced Python.
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Filter by title and date
        from_date = datetime(2023, 1, 1)
        filtered = manager.filter_posts(title_pattern="python", from_date=from_date)
        assert len(filtered) == 1
        assert filtered[0].get_title() == "Python Tutorial 2023"


def test_hugo_post_manager_nonexistent_directory():
    """Test loading posts from non-existent directory."""
    content_dir = Path("/nonexistent/directory/path")
    manager = HugoPostManager(content_dir)

    with pytest.raises(SystemExit) as exc_info:
        manager.load_posts()
    assert exc_info.value.code == 1


def test_hugo_post_get_metadata_list_dict():
    """Test get_metadata_list with non-list, non-string value (returns empty)."""
    content = """---
title: Test Post
metadata: {key: value}
---
Content
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        # get_metadata_list should return empty for dict values
        result = post.get_metadata_list("metadata")
        assert result == []
    finally:
        temp_path.unlink()


def test_hugo_post_get_full_text():
    """Test get_full_text method."""
    content = """---
title: Test Post
tags:
  - python
---

Post content here.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        full_text = post.get_full_text()
        assert "title: Test Post" in full_text
        assert "python" in full_text
        assert "Post content here" in full_text
    finally:
        temp_path.unlink()


def test_hugo_post_save_toml_with_datetime():
    """Test saving TOML with datetime conversion."""
    content = """+++
title = "Test Post"
date = 2023-01-15T10:30:00Z
+++

Content
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        post = HugoPost(temp_path)
        # Modify and save
        post.set_metadata_list("tags", ["python"])
        post.save()

        # Re-read and verify
        saved_content = temp_path.read_text()
        assert "+++" in saved_content
        assert "python" in saved_content
    finally:
        temp_path.unlink()


def test_hugo_post_filter_text_pattern():
    """Test filtering by text content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        (content_dir / "post1.md").write_text(
            """---
title: Post 1
---
This post discusses machine learning.
"""
        )
        (content_dir / "post2.md").write_text(
            """---
title: Post 2
---
This is about web development.
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Filter by text content
        filtered = manager.filter_posts(text_pattern="machine learning")
        assert len(filtered) == 1
        assert filtered[0].get_title() == "Post 1"


def test_hugo_post_filter_to_date():
    """Test filtering with to_date."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        (content_dir / "old.md").write_text(
            """---
title: Old Post
date: 2020-01-01
---
Content
"""
        )
        (content_dir / "new.md").write_text(
            """---
title: New Post
date: 2023-12-31
---
Content
"""
        )

        manager = HugoPostManager(content_dir)
        manager.load_posts()

        # Filter by to_date
        to_date = datetime(2022, 1, 1)
        filtered = manager.filter_posts(to_date=to_date)
        assert len(filtered) == 1
        assert filtered[0].get_title() == "Old Post"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
