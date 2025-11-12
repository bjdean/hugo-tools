# Contributing to Hugo Tools

Thank you for considering contributing to Hugo Tools! This document provides guidelines for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/bjdean/hugo-tools.git
cd hugo-tools
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with dev dependencies:
```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hugotools --cov-report=html

# Run specific test file
pytest tests/test_common.py

# Run specific test
pytest tests/test_common.py::test_hugo_post_parsing
```

## Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting

Format code before committing:
```bash
black src/ tests/
ruff check src/ tests/
```

## Making Changes

1. Create a new branch:
```bash
git checkout -b feature/my-new-feature
```

2. Make your changes

3. Add tests for new functionality

4. Run tests and ensure they pass:
```bash
pytest
```

5. Format code:
```bash
black src/ tests/
```

6. Commit changes:
```bash
git add .
git commit -m "Add feature: description of feature"
```

7. Push to your fork:
```bash
git push origin feature/my-new-feature
```

8. Create a Pull Request

## Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests liberally

Examples:
```
Add WordPress import dry-run mode
Fix datetime sync for posts without dates
Update documentation for tag command
```

## Pull Request Process

1. Update README.md with details of changes if applicable
2. Update docs/README.md with any new command options
3. Add tests for new functionality
4. Ensure all tests pass
5. Update version number in `src/hugotools/version.py` if appropriate

## Adding New Commands

To add a new command:

1. Create command module in `src/hugotools/commands/`:
```python
# src/hugotools/commands/my_command.py
def run(args=None):
    """Run the my_command command."""
    parser = argparse.ArgumentParser(
        prog='hugotools my_command',
        description='Description of command'
    )
    # Add arguments
    parsed_args = parser.parse_args(args)
    # Implement command logic
    return 0
```

2. Update `src/hugotools/cli.py` to register the command

3. Add tests in `tests/test_my_command.py`

4. Update documentation in `README.md` and `docs/README.md`

## Testing Guidelines

- Write tests for all new functionality
- Aim for high coverage (>80%)
- Use temporary directories for file operations
- Clean up resources after tests
- Test both success and failure cases
- Test edge cases

Example test structure:
```python
def test_my_feature():
    """Test description."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        content_dir = Path(tmpdir) / 'posts'
        content_dir.mkdir()

        # Create test data
        post_file = content_dir / 'test.md'
        post_file.write_text("...")

        # Execute
        result = my_function(content_dir)

        # Assert
        assert result == expected_value
```

## Documentation

- Update README.md for user-facing changes
- Update docs/README.md for detailed documentation
- Add docstrings to all functions and classes
- Include usage examples

## Release Process

1. Update version in `src/hugotools/version.py`
2. Update CHANGELOG.md (if created)
3. Create git tag:
```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```
4. Build and publish to PyPI:
```bash
python -m build
twine upload dist/*
```

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about development
- Suggestions for improvements

## Code of Conduct

Be respectful and professional in all interactions. We welcome contributions from everyone.
