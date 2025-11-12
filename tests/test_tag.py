"""Tests for tag command."""

import tempfile
from pathlib import Path

import pytest
from hugotools.commands.tag import HugoTagManager


def test_tag_manager_add_tags():
    """Test adding tags to posts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        post_file = content_dir / 'test-post.md'
        post_file.write_text("""---
title: Test Post
tags:
  - existing
---

Content.
""")

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_metadata(
            manager.posts,
            'tags',
            add_items={'new-tag'},
            remove_items=set(),
            dry_run=False
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        tags = manager2.posts[0].get_metadata_list('tags')

        assert 'existing' in tags
        assert 'new-tag' in tags


def test_tag_manager_remove_tags():
    """Test removing tags from posts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        post_file = content_dir / 'test-post.md'
        post_file.write_text("""---
title: Test Post
tags:
  - keep
  - remove
---

Content.
""")

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_metadata(
            manager.posts,
            'tags',
            add_items=set(),
            remove_items={'remove'},
            dry_run=False
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        tags = manager2.posts[0].get_metadata_list('tags')

        assert 'keep' in tags
        assert 'remove' not in tags


def test_tag_manager_dry_run():
    """Test dry run mode doesn't modify files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        post_file = content_dir / 'test-post.md'
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
            manager.posts,
            'tags',
            add_items={'new-tag'},
            remove_items=set(),
            dry_run=True
        )

        assert modified == 1

        # Verify file was not modified
        assert post_file.read_text() == original_content


def test_tag_manager_label_fields():
    """Test setting single-value label fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        post_file = content_dir / 'test-post.md'
        post_file.write_text("""---
title: Test Post
---

Content.
""")

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_label(
            manager.posts,
            'status',
            set_value='published',
            remove=False,
            dry_run=False
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        status = manager2.posts[0].get_metadata_label('status')

        assert status == 'published'


def test_tag_manager_categories():
    """Test working with categories field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        post_file = content_dir / 'test-post.md'
        post_file.write_text("""---
title: Test Post
categories:
  - Tech
---

Content.
""")

        manager = HugoTagManager(content_dir)
        manager.load_posts()

        modified = manager.modify_metadata(
            manager.posts,
            'categories',
            add_items={'Programming'},
            remove_items=set(),
            dry_run=False
        )

        assert modified == 1

        # Re-read and verify
        manager2 = HugoTagManager(content_dir)
        manager2.load_posts()
        categories = manager2.posts[0].get_metadata_list('categories')

        assert 'Tech' in categories
        assert 'Programming' in categories


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
