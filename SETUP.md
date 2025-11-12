# Hugo Tools Setup Guide

This guide covers installing, testing, and publishing the Hugo Tools package.

## Local Development & Testing

### 1. Install in Development Mode

From the `hugo-tools-package` directory:

```bash
# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"
```

This installs the package in "editable" mode, meaning changes to source code are immediately reflected without reinstalling.

### 2. Verify Installation

```bash
# Check that hugotools command is available
hugotools --help

# You should see the main help with available commands
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=hugotools --cov-report=html

# Open coverage report (optional)
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 4. Test Commands Locally

```bash
# Test on your actual Hugo site
cd /path/to/your/hugo/site

# Test datetime sync (dry run first!)
hugotools datetime --all --dry-run

# Test tag management
hugotools tag --all --dump

# If you have a WordPress export, test import
hugotools import wordpress-export.xml --dry-run --limit 5
```

## Publishing to PyPI

### First Time Setup

1. Create accounts:
   - PyPI: https://pypi.org/account/register/
   - TestPyPI: https://test.pypi.org/account/register/

2. Install build tools:
```bash
pip install build twine
```

3. Create `~/.pypirc` file:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

### Test Release (TestPyPI)

```bash
# Build the package
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ hugotools
```

### Production Release (PyPI)

```bash
# Make sure everything is committed
git status

# Update version in src/hugotools/version.py
# Example: __version__ = "0.1.0" -> "0.1.1"

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*

# Create git tag
git tag -a v0.1.1 -m "Release version 0.1.1"
git push origin v0.1.1
```

## GitHub Setup

### 1. Create Repository

```bash
cd hugo-tools-package
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/hugo-tools.git
git branch -M main
git push -u origin main
```

### 2. Update URLs in pyproject.toml

Edit `pyproject.toml` and replace placeholder URLs:

```toml
[project.urls]
Homepage = "https://github.com/YOUR-USERNAME/hugo-tools"
Repository = "https://github.com/YOUR-USERNAME/hugo-tools"
Issues = "https://github.com/YOUR-USERNAME/hugo-tools/issues"
```

### 3. Add GitHub Actions (Optional)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        pytest --cov=hugotools
    - name: Run linting
      run: |
        ruff check src/
```

## Directory Structure

```
hugo-tools-package/
├── src/
│   └── hugotools/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py           # Main CLI router
│       ├── common.py         # Shared utilities
│       ├── version.py
│       └── commands/
│           ├── __init__.py
│           ├── datetime.py
│           ├── tag.py
│           └── import_wordpress.py
├── tests/
│   ├── __init__.py
│   ├── test_common.py
│   ├── test_datetime.py
│   ├── test_tag.py
│   └── test_import_wordpress.py
├── docs/
│   └── README.md
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── MANIFEST.in
├── CONTRIBUTING.md
└── SETUP.md (this file)
```

## Version Numbering

Follow Semantic Versioning (semver.org):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): New features, backwards compatible
- **PATCH** version (0.0.1): Backwards compatible bug fixes

## Checklist Before Release

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] No linting errors: `ruff check src/`
- [ ] Version number updated in `src/hugotools/version.py`
- [ ] README.md is up to date
- [ ] CONTRIBUTING.md is clear
- [ ] All changes committed to git
- [ ] Tested on real Hugo site
- [ ] Documentation is complete

## Common Issues

### ModuleNotFoundError after installation

Make sure you're in the package directory when running `pip install -e .`

### Command not found: hugotools

- Deactivate and reactivate virtual environment
- Check `pip show hugotools` to verify installation
- Ensure virtual environment's bin directory is in PATH

### Tests fail with import errors

Install dev dependencies: `pip install -e ".[dev]"`

### Upload to PyPI fails

- Check your API token is correct in `~/.pypirc`
- Ensure you've built the package: `python -m build`
- Try uploading to TestPyPI first

## Support

- Issues: https://github.com/bjdean/hugo-tools/issues
- Email: bj@bjdean.id.au
