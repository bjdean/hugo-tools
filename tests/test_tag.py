"""Tests for tag command."""

import tempfile
from pathlib import Path

import pytest

from hugotools.commands.tag import HugoTagManager


def test_tag_manager_add_tags():
    """Test adding tags to posts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
tags:
  - existing
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_metadata(
            manager.posts, "tags", add_items={"new-tag"}, remove_items=set(), dry_run=False
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        tags = manager2.posts[0].get_metadata_list("tags")

        assert "existing" in tags
        assert "new-tag" in tags


def test_tag_manager_remove_tags():
    """Test removing tags from posts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
tags:
  - keep
  - remove
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_metadata(
            manager.posts, "tags", add_items=set(), remove_items={"remove"}, dry_run=False
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        tags = manager2.posts[0].get_metadata_list("tags")

        assert "keep" in tags
        assert "remove" not in tags


def test_tag_manager_dry_run():
    """Test dry run mode doesn't modify files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        original_content = """---
title: Test Post
tags:
  - original
---

Content.
"""
        post_file.write_text(original_content)

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_metadata(
            manager.posts, "tags", add_items={"new-tag"}, remove_items=set(), dry_run=True
        )

        assert modified == 1

        # Verify file was not modified
        assert post_file.read_text() == original_content


def test_tag_manager_label_fields():
    """Test setting single-value label fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_label(
            manager.posts, "status", set_value="published", remove=False, dry_run=False
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        status = manager2.posts[0].get_metadata_label("status")

        assert status == "published"


def test_tag_manager_categories():
    """Test working with categories field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
categories:
  - Tech
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_metadata(
            manager.posts,
            "categories",
            add_items={"Programming"},
            remove_items=set(),
            dry_run=False,
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        categories = manager2.posts[0].get_metadata_list("categories")

        assert "Tech" in categories
        assert "Programming" in categories


def test_tag_manager_label_remove():
    """Test removing a label field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
status: draft
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_label(
            manager.posts, "status", set_value=None, remove=True, dry_run=False
        )

        assert modified == 1

        # Re-read and verify field is removed
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        status = manager2.posts[0].get_metadata_label("status")

        assert status is None


def test_tag_run_with_args():
    """Test running tag command with arguments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
tags:
  - python
---

Content.
"""
        )

        from hugotools.commands.tag import run

        result = run(["--all", "--add", "tutorial", "--content-dir", str(content_dir), "--dry-run"])
        assert result == 0


def test_tag_run_no_selection_error():
    """Test that run() fails when no selection criteria provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(["--add", "test", "--content-dir", str(content_dir)])
        assert exc_info.value.code != 0


def test_tag_run_dump_mode():
    """Test dump mode reports values without modifying."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        original_content = """---
title: Test Post
tags:
  - python
  - tutorial
---

Content.
"""
        post_file.write_text(original_content)

        from hugotools.commands.tag import run

        result = run(["--all", "--dump", "--content-dir", str(content_dir)])
        assert result == 0

        # Verify file was not modified
        assert post_file.read_text() == original_content


def test_tag_run_categories():
    """Test running with categories field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
categories:
  - Tech
---

Content.
"""
        )

        from hugotools.commands.tag import run

        result = run(["--all", "--categories", "--add", "Programming", "--content-dir", str(content_dir), "--dry-run"])
        assert result == 0


def test_tag_run_custom_label():
    """Test running with custom label field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
---

Content.
"""
        )

        from hugotools.commands.tag import run

        result = run(["--all", "--custom-label", "author", "--set", "John Doe", "--content-dir", str(content_dir), "--dry-run"])
        assert result == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
