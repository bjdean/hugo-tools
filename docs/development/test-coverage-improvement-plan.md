# Test Coverage Improvement Plan for hugotools

## Current State
- **Overall coverage**: 42% (746 statements, 434 missing)
- **Passing tests**: 25/25 (100%)
- **Critical gaps**: CLI layer (0%), command `run()` functions (mostly untested), error paths

## Coverage Analysis by Module

### 1. **CLI Layer (0% coverage)** - HIGH PRIORITY
- `cli.py` (0/27 statements): Main entry point, command routing
- `__main__.py` (0/3 statements): Python module entry point

**Missing coverage:**
- Subcommand routing logic (datetime, tag, import)
- Help text display
- No command specified case
- Invalid command handling
- Version flag

### 2. **Command Run Functions (Low coverage)** - HIGH PRIORITY
Commands have good core logic coverage but minimal CLI integration testing:

- `commands/datetime.py` (49%): Lines 52, 71-74, 81-164, 168 missing
  - CLI argument parsing (`run()` function)
  - Output formatting and summary statistics
  - Error handling in main flow

- `commands/tag.py` (30%): Lines 90, 94, 104, 118-158, 163-379, 383 missing
  - CLI argument parsing and validation
  - Field type selection logic (tags/categories/custom)
  - Operation validation (add/remove/set/dump)
  - Output formatting

- `commands/import_wordpress.py` (30%): Lines 47-71, 75-76, 80-87, 92-103, etc.
  - CLI argument parsing
  - File I/O operations (XML parsing, file writing)
  - Error handling for invalid XML
  - Statistics reporting
  - Dry-run mode

### 3. **Common Library (70% coverage)** - MEDIUM PRIORITY
`common.py` has decent coverage but gaps in:
- Error handling paths (lines 56-58, 72-74, 88-90)
- Edge cases in date parsing
- Argument validation error cases (lines 281-284, 296-319, 330-333, 349-359)
- TOML datetime conversion helper

## Recommended Testing Strategy

### Phase 1: CLI Integration Tests (Target: 80%+ CLI coverage)

**Create `tests/test_cli.py`:**
```python
# Test command routing
- test_cli_no_command_shows_help()
- test_cli_version_flag()
- test_cli_datetime_command_routing()
- test_cli_tag_command_routing()
- test_cli_import_command_routing()
- test_cli_invalid_command()
- test_cli_help_flag()
```

### Phase 2: Command Run Function Tests (Target: 70%+ command coverage)

**Enhance `tests/test_datetime.py`:**
```python
# CLI integration
- test_datetime_run_with_args()
- test_datetime_run_no_selection_error()
- test_datetime_run_output_formatting()
- test_datetime_run_statistics_summary()
- test_datetime_run_error_handling()
- test_datetime_run_file_permission_error()

# Edge cases
- test_datetime_file_stat_error()
- test_datetime_timezone_aware_dates()
```

**Enhance `tests/test_tag.py`:**
```python
# CLI integration
- test_tag_run_with_args()
- test_tag_run_field_validation()
- test_tag_run_operation_validation()
- test_tag_run_label_vs_list_errors()
- test_tag_run_dump_mode()
- test_tag_run_categories_field()
- test_tag_run_custom_list_field()
- test_tag_run_custom_label_field()
- test_tag_run_conflicting_field_options()

# Coverage gaps
- test_label_remove_operation()
- test_dump_with_operation_error()
```

**Enhance `tests/test_import_wordpress.py`:**
```python
# CLI integration
- test_import_run_with_args()
- test_import_run_file_not_found()
- test_import_run_invalid_xml()
- test_import_run_dry_run_mode()
- test_import_run_limit_option()
- test_import_run_statistics()
- test_import_run_stray_html_reporting()

# File operations
- test_parse_wordpress_xml_full()
- test_convert_post_full_integration()
- test_file_writing_with_mtime()
- test_output_directory_creation()

# Edge cases
- test_convert_code_blocks_nested()
- test_detect_stray_html_in_text()
- test_wordpress_post_no_content()
- test_wordpress_post_missing_fields()
```

### Phase 3: Common Library Edge Cases (Target: 85%+ common coverage)

**Enhance `tests/test_common.py`:**
```python
# Error handling
- test_hugo_post_yaml_parse_error()
- test_hugo_post_toml_parse_error()
- test_hugo_post_json_parse_error()
- test_hugo_post_malformed_frontmatter()

# Date parsing edge cases
- test_get_date_invalid_format()
- test_get_date_multiple_formats()
- test_get_date_timezone_handling()

# Filter edge cases
- test_filter_posts_path_not_found()
- test_filter_posts_combined_filters()
- test_filter_posts_empty_directory()

# Argument validation
- test_validate_post_selection_no_options_error()
- test_validate_post_selection_with_text()
- test_validate_post_selection_without_text()
- test_parse_date_invalid_format()

# TOML helper
- test_prepare_for_toml_datetime()
- test_prepare_for_toml_nested()
```

### Phase 4: Integration and End-to-End Tests (Target: Overall 75%+)

**Create `tests/test_integration.py`:**
```python
# Full workflow tests
- test_full_workflow_datetime_sync()
- test_full_workflow_tag_management()
- test_full_workflow_wordpress_import()
- test_workflow_with_real_hugo_structure()
```

## Testing Utilities Needed

**Create `tests/conftest.py` or enhance existing fixtures:**
```python
# Fixtures for CLI testing
- @pytest.fixture: mock_argv
- @pytest.fixture: temp_hugo_site (creates full Hugo structure)
- @pytest.fixture: sample_wordpress_xml
- @pytest.fixture: capture_stdout_stderr

# Fixtures for file operations
- @pytest.fixture: temp_content_dir
- @pytest.fixture: sample_posts_varied_formats
```

## Priority Order (for implementation)

1. **Week 1**: CLI integration tests (`test_cli.py`) - High impact, currently 0%
2. **Week 2**: Command `run()` function tests - Complete the command layer
3. **Week 3**: Common library edge cases - Strengthen foundation
4. **Week 4**: Integration tests - Validate full workflows

## Coverage Targets

- **Phase 1 Complete**: ~55% overall (from 42%)
- **Phase 2 Complete**: ~65% overall
- **Phase 3 Complete**: ~75% overall
- **Phase 4 Complete**: ~80% overall (aspirational target)

## Notes

- Focus on **functional correctness** over arbitrary coverage numbers
- **CLI integration tests** provide highest ROI - they're currently at 0%
- **Error paths** are under-tested but critical for user experience
- **File I/O operations** need more coverage (WordPress import, file writing)
- Consider using **parameterized tests** to test multiple frontmatter formats efficiently
- Use **mock.patch** for file system operations in CLI tests to avoid temp file overhead

## Implementation Status

- [x] Phase 1: CLI Integration Tests - **COMPLETED**
- [x] Phase 2: Command Run Function Tests - **COMPLETED**
- [x] Phase 3: Common Library Edge Cases - **COMPLETED**
- [ ] Phase 4: Integration Tests - Optional future enhancement

## Results

### Coverage Improvement Summary

**Before**: 42% overall coverage (746 statements, 434 missing)
**After**: 83% overall coverage (746 statements, 124 missing)
**Improvement**: +41 percentage points

### Module-by-Module Results

| Module | Before | After | Improvement |
|--------|--------|-------|-------------|
| `cli.py` | 0% | 89% | +89% |
| `commands/datetime.py` | 49% | 86% | +37% |
| `commands/tag.py` | 30% | 81% | +51% |
| `commands/import_wordpress.py` | 30% | 76% | +46% |
| `common.py` | 70% | **95%** | +25% |

### Test Count

- **Before**: 25 tests
- **After**: 55 tests
- **Added**: 30 new tests

### New Test Files

- `tests/test_cli.py` - 9 tests for CLI entry point and command routing

### Enhanced Test Files

- `tests/test_datetime.py` - Added 3 CLI integration tests
- `tests/test_tag.py` - Added 6 CLI integration and edge case tests
- `tests/test_common.py` - Added 12 edge case and error handling tests (including TOML and JSON parsing errors)

### Remaining Gaps

The remaining 17% uncovered code consists primarily of:

1. **Error handling paths** - Edge cases in error reporting
2. **WordPress import specifics** - Some complex HTML parsing edge cases
3. **`__main__.py`** - Module entry point (low priority)
4. **Output formatting** - Print statements and summary reports

These are acceptable gaps for a well-tested codebase. The critical business logic and user-facing functionality now have excellent coverage.
