"""Tests for datetime command."""

import tempfile
import os
from pathlib import Path
from datetime import datetime

import pytest
from hugotools.commands.datetime import DatetimeSynchronizer


def test_datetime_synchronizer_basic():
    """Test basic datetime synchronization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        # Create a test post with a specific date
        post_file = content_dir / 'test-post.md'
        post_file.write_text("""---
title: Test Post
date: 2023-06-15 14:30:00
---

Test content.
""")

        # Set file mtime to something different
        old_time = datetime(2020, 1, 1).timestamp()
        os.utime(post_file, (old_time, old_time))

        # Synchronize
        synchronizer = DatetimeSynchronizer(content_dir)
        synchronizer.load_posts()

        modified, skipped, errors = synchronizer.synchronize_datetimes(
            synchronizer.posts,
            dry_run=False
        )

        assert modified == 1
        assert skipped == 0
        assert errors == 0

        # Verify file mtime was updated
        new_mtime = datetime.fromtimestamp(post_file.stat().st_mtime)
        assert new_mtime.year == 2023
        assert new_mtime.month == 6
        assert new_mtime.day == 15


def test_datetime_synchronizer_dry_run():
    """Test dry run mode doesn't modify files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        post_file = content_dir / 'test-post.md'
        post_file.write_text("""---
title: Test Post
date: 2023-06-15 14:30:00
---

Test content.
""")

        old_time = datetime(2020, 1, 1).timestamp()
        os.utime(post_file, (old_time, old_time))

        original_mtime = post_file.stat().st_mtime

        # Dry run
        synchronizer = DatetimeSynchronizer(content_dir)
        synchronizer.load_posts()

        modified, skipped, errors = synchronizer.synchronize_datetimes(
            synchronizer.posts,
            dry_run=True
        )

        assert modified == 1

        # Verify file was NOT modified
        assert post_file.stat().st_mtime == original_mtime


def test_datetime_synchronizer_skips_no_date():
    """Test skipping posts without valid dates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        post_file = content_dir / 'test-post.md'
        post_file.write_text("""---
title: Test Post
---

No date field.
""")

        synchronizer = DatetimeSynchronizer(content_dir)
        synchronizer.load_posts()

        modified, skipped, errors = synchronizer.synchronize_datetimes(
            synchronizer.posts,
            dry_run=False
        )

        assert modified == 0
        assert skipped == 1
        assert errors == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
