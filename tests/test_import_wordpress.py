"""Tests for WordPress import command."""

import tempfile
from pathlib import Path

import pytest
from hugotools.commands.import_wordpress import (
    WordPressPost,
    clean_html_entities,
    convert_code_blocks,
    convert_images,
    detect_stray_html,
    generate_filename,
)


def test_clean_html_entities():
    """Test HTML entity conversion."""
    text = "Hello &amp; goodbye &lt;tag&gt;"
    result = clean_html_entities(text)
    assert result == "Hello & goodbye <tag>"


def test_convert_code_blocks():
    """Test code block conversion."""
    html = """
<p>Some text</p>
<pre><code class="language-python">print("hello")</code></pre>
<p>More text</p>
"""
    result, code_blocks = convert_code_blocks(html)

    assert '___CODEBLOCK_0___' in result
    assert len(code_blocks) == 1
    assert '```python' in code_blocks[0]
    assert 'print("hello")' in code_blocks[0]


def test_convert_images():
    """Test image conversion."""
    html = '<p>Text <img src="image.jpg" alt="My Image"> more text</p>'
    result = convert_images(html)

    assert '![My Image](image.jpg)' in result


def test_detect_stray_html():
    """Test detection of unconverted HTML."""
    markdown = """
# Title

Normal content here.

```python
# Code with <brackets> should be ignored
```

<div>This is a problem</div>
"""
    tags = detect_stray_html(markdown)
    assert 'div' in tags
    # Brackets in code blocks should be ignored


def test_generate_filename():
    """Test filename generation."""
    # Mock WordPressPost object
    class MockPost:
        def __init__(self):
            self.post_name = "my-awesome-post"
            self.title = "My Awesome Post!"

    post = MockPost()
    filename = generate_filename(post)

    assert filename == "my-awesome-post.md"


def test_generate_filename_from_title():
    """Test filename generation from title when post_name missing."""
    class MockPost:
        def __init__(self):
            self.post_name = ""
            self.title = "Hello World! 2023"

    post = MockPost()
    filename = generate_filename(post)

    assert filename == "hello-world-2023.md"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
