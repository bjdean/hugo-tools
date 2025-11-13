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

        result = run(
            [
                "--all",
                "--categories",
                "--add",
                "Programming",
                "--content-dir",
                str(content_dir),
                "--dry-run",
            ]
        )
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

        result = run(
            [
                "--all",
                "--custom-label",
                "author",
                "--set",
                "John Doe",
                "--content-dir",
                str(content_dir),
                "--dry-run",
            ]
        )
        assert result == 0


def test_tag_run_conflicting_field_options():
    """Test error when multiple field options are specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(
                [
                    "--all",
                    "--categories",
                    "--custom-list",
                    "keywords",
                    "--add",
                    "test",
                    "--content-dir",
                    str(content_dir),
                ]
            )
        assert exc_info.value.code != 0


def test_tag_run_label_with_add_error():
    """Test error when using --add with label field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(
                [
                    "--all",
                    "--custom-label",
                    "status",
                    "--add",
                    "published",
                    "--content-dir",
                    str(content_dir),
                ]
            )
        assert exc_info.value.code != 0


def test_tag_run_list_with_set_error():
    """Test error when using --set with list field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(["--all", "--set", "value", "--content-dir", str(content_dir)])
        assert exc_info.value.code != 0


def test_tag_run_dump_with_add_error():
    """Test error when using --dump with --add."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(["--all", "--dump", "--add", "test", "--content-dir", str(content_dir)])
        assert exc_info.value.code != 0


def test_tag_run_no_operation_error():
    """Test error when no operation is specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(["--all", "--content-dir", str(content_dir)])
        assert exc_info.value.code != 0


def test_tag_dump_with_empty_values():
    """Test dump mode with posts that have empty tag values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
---

Content without tags.
"""
        )

        from hugotools.commands.tag import run

        # Should handle empty/missing values gracefully
        result = run(["--all", "--dump", "--content-dir", str(content_dir)])
        assert result == 0


def test_tag_dump_label_with_missing_values():
    """Test dump mode for label field with some posts missing the field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        (content_dir / "with-author.md").write_text(
            """---
title: Post With Author
author: John Doe
---
Content
"""
        )
        (content_dir / "without-author.md").write_text(
            """---
title: Post Without Author
---
Content
"""
        )

        from hugotools.commands.tag import run

        # Should handle missing values gracefully
        result = run(
            ["--all", "--custom-label", "author", "--dump", "--content-dir", str(content_dir)]
        )
        assert result == 0


def test_tag_copy_list_fields():
    """Test copying from one list field to another."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
categories:
  - Tech
  - Programming
tags:
  - python
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.copy_or_move_metadata(
            manager.posts,
            source_field="categories",
            source_type="list",
            dest_field="tags",
            dest_type="list",
            move=False,
            dry_run=False,
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        tags = manager2.posts[0].get_metadata_list("tags")
        categories = manager2.posts[0].get_metadata_list("categories")

        # Tags should have original + copied values
        assert "python" in tags
        assert "Tech" in tags
        assert "Programming" in tags

        # Categories should be unchanged (copy, not move)
        assert "Tech" in categories
        assert "Programming" in categories


def test_tag_move_list_fields():
    """Test moving from one list field to another."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
categories:
  - Tech
  - Programming
tags:
  - python
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.copy_or_move_metadata(
            manager.posts,
            source_field="categories",
            source_type="list",
            dest_field="tags",
            dest_type="list",
            move=True,
            dry_run=False,
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        tags = manager2.posts[0].get_metadata_list("tags")
        categories = manager2.posts[0].get_metadata_list("categories")

        # Tags should have original + moved values
        assert "python" in tags
        assert "Tech" in tags
        assert "Programming" in tags

        # Categories should be empty (moved)
        assert len(categories) == 0


def test_tag_copy_label_fields():
    """Test copying from one label field to another."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
author: John Doe
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.copy_or_move_metadata(
            manager.posts,
            source_field="author",
            source_type="label",
            dest_field="editor",
            dest_type="label",
            move=False,
            dry_run=False,
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        author = manager2.posts[0].get_metadata_label("author")
        editor = manager2.posts[0].get_metadata_label("editor")

        # Both should have the value (copy, not move)
        assert author == "John Doe"
        assert editor == "John Doe"


def test_tag_move_label_fields():
    """Test moving from one label field to another."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
author: John Doe
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.copy_or_move_metadata(
            manager.posts,
            source_field="author",
            source_type="label",
            dest_field="editor",
            dest_type="label",
            move=True,
            dry_run=False,
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        author = manager2.posts[0].get_metadata_label("author")
        editor = manager2.posts[0].get_metadata_label("editor")

        # Author should be removed, editor should have the value
        assert author is None
        assert editor == "John Doe"


def test_tag_copy_incompatible_types_error():
    """Test error when trying to copy between incompatible field types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
categories:
  - Tech
author: John Doe
---

Content.
"""
        )

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        # Try to copy from list to label - should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            manager.copy_or_move_metadata(
                manager.posts,
                source_field="categories",
                source_type="list",
                dest_field="author",
                dest_type="label",
                move=False,
                dry_run=False,
            )

        assert "Cannot copy/move between different field types" in str(exc_info.value)


def test_tag_copy_dry_run():
    """Test copy in dry run mode doesn't modify files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        original_content = """---
title: Test Post
categories:
  - Tech
tags:
  - python
---

Content.
"""
        post_file.write_text(original_content)

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.copy_or_move_metadata(
            manager.posts,
            source_field="categories",
            source_type="list",
            dest_field="tags",
            dest_type="list",
            move=False,
            dry_run=True,
        )

        assert modified == 1

        # Verify file was not modified
        assert post_file.read_text() == original_content


def test_tag_copy_empty_source():
    """Test copy with empty source field doesn't modify anything."""
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

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        # Try to copy from categories (which doesn't exist) to tags
        modified = manager.copy_or_move_metadata(
            manager.posts,
            source_field="categories",
            source_type="list",
            dest_field="tags",
            dest_type="list",
            move=False,
            dry_run=False,
        )

        # Should not modify anything
        assert modified == 0

        # Re-read and verify tags unchanged
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        tags = manager2.posts[0].get_metadata_list("tags")

        assert tags == ["python"]


def test_tag_run_copy_categories_to_tags():
    """Test running copy command with categories to tags."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
categories:
  - Tech
  - Programming
tags:
  - python
---

Content.
"""
        )

        from hugotools.commands.tag import run

        result = run(["--all", "--copy", "categories", "--content-dir", str(content_dir)])
        assert result == 0

        # Verify the copy worked
        manager = HugoTagManager(content_dir)
        manager.load_posts()
        tags = manager.posts[0].get_metadata_list("tags")
        categories = manager.posts[0].get_metadata_list("categories")

        assert "python" in tags
        assert "Tech" in tags
        assert "Programming" in tags
        assert "Tech" in categories
        assert "Programming" in categories


def test_tag_run_move_tags_to_categories():
    """Test running move command with tags to categories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        post_file = content_dir / "test-post.md"
        post_file.write_text(
            """---
title: Test Post
categories:
  - Tech
tags:
  - python
  - tutorial
---

Content.
"""
        )

        from hugotools.commands.tag import run

        result = run(["--all", "--move", "tags", "--categories", "--content-dir", str(content_dir)])
        assert result == 0

        # Verify the move worked
        manager = HugoTagManager(content_dir)
        manager.load_posts()
        tags = manager.posts[0].get_metadata_list("tags")
        categories = manager.posts[0].get_metadata_list("categories")

        # Tags should be empty
        assert len(tags) == 0

        # Categories should have original + moved values
        assert "Tech" in categories
        assert "python" in categories
        assert "tutorial" in categories


def test_tag_run_copy_and_move_error():
    """Test error when using both --copy and --move."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(
                [
                    "--all",
                    "--copy",
                    "categories",
                    "--move",
                    "tags",
                    "--content-dir",
                    str(content_dir),
                ]
            )
        assert exc_info.value.code != 0


def test_tag_run_copy_with_add_error():
    """Test error when using --copy with --add."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / "posts"
        content_dir.mkdir()

        from hugotools.commands.tag import run

        with pytest.raises(SystemExit) as exc_info:
            run(
                [
                    "--all",
                    "--copy",
                    "categories",
                    "--add",
                    "test",
                    "--content-dir",
                    str(content_dir),
                ]
            )
        assert exc_info.value.code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
