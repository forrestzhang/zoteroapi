# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **zoteroapi** - a Python client library for accessing the local Zotero server API. The library provides a clean interface to interact with Zotero's local server functionality for managing academic references, collections, notes, and files.

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/zoteroapi --cov-report=term-missing

# Generate coverage HTML report
pytest --cov=src/zoteroapi --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py

# Run specific test function
pytest tests/unit/test_client.py::TestZoteroLocal::test_get_items_top

# Run tests with verbose output
pytest -v

# Run with detailed output (show local variables)
pytest -v -s

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests with specific markers
pytest -m "unit"
pytest -m "integration"
pytest -m "slow"
pytest -m "network"

# Run tests in parallel (faster execution)
pytest -n auto

# Run tests with xfail for expected failures
pytest --xfail

# Stop on first failure
pytest -x

# Run tests with custom pytest configuration
pytest -c custom_pytest.ini

# Check test coverage requirements (minimum 85%)
pytest --cov=src/zoteroapi --cov-fail-under=85
```

### Documentation
```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve

# Deploy documentation (if configured)
mkdocs gh-deploy
```

### Code Quality & Linting
```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/

# Run all quality checks together
black src/ tests/ && ruff check src/ tests/ && mypy src/

# Fix auto-fixable issues
ruff check --fix src/ tests/
black src/ tests/
```

### Package Management
```bash
# Install development dependencies (includes test and docs)
pip install -e ".[test,docs]"

# Install only test dependencies
pip install -e ".[test]"

# Install only documentation dependencies
pip install -e ".[docs]"

# Build package
python -m build

# Install package in development mode
pip install -e .

# Build and upload to PyPI (requires credentials)
python -m build
twine upload dist/*
```

## Architecture

### Core Components

**BaseZoteroClient** (`src/zoteroapi/base_client.py`)
- Foundation class that handles HTTP requests to Zotero's local server
- Manages session handling, request/response processing, and error handling
- Uses `requests.Session` for connection pooling
- Default URL: `http://localhost:23119/api/users/000000/`

**ZoteroLocal** (`src/zoteroapi/client.py`)
- Main client class that inherits from BaseZoteroClient
- Implements Mixin pattern to modularize functionality
- Primary interface for end-users

**Mixin Classes** (`src/zoteroapi/mixins/`)
- **SearchMixin**: Search functionality (keywords, DOI, PMID, title)
- **FilesMixin**: File operations (download, upload, attachment handling)
- **NotesMixin**: Note management and operations

**Exceptions** (`src/zoteroapi/exceptions.py`)
- `ZoteroLocalError`: Base exception class
- `ConnectionError`, `AuthenticationError`, `NotFoundError`
- `APIError`, `ResourceNotFound`

### Project Structure
```
src/zoteroapi/
├── __init__.py          # Package initialization, exports main classes
├── base_client.py       # HTTP request handling foundation
├── client.py           # Main ZoteroLocal client implementation
├── exceptions.py       # Custom exception hierarchy
└── mixins/
    ├── search.py       # Search functionality
    ├── files.py        # File operations
    └── notes.py        # Note management

tests/                  # Comprehensive test suite
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for workflows
├── fixtures/          # Test data and mock responses
└── utils/             # Test utilities

examples/              # Usage examples and tutorials
```

## Key Design Patterns

### Mixin Pattern
The library uses mixins to modularize functionality:
- Each mixin focuses on a specific domain (search, files, notes)
- Mixins are independent and can be combined as needed
- ZoteroLocal inherits from BaseZoteroClient and all mixins

### Error Handling
- All API operations raise `ZoteroLocalError` or its subclasses
- HTTP errors are translated to appropriate exception types
- 404 responses raise `ResourceNotFound`
- Connection issues raise `ConnectionError`

### API Response Format
- All API responses default to JSON format (`format=json` parameter)
- Response structure follows Zotero API v3 specification
- Items have standardized structure with `data`, `meta`, and `links` fields
- Error responses are translated to appropriate exception classes
- Session management handled by BaseZoteroClient with connection pooling

### Session Management
- Uses `requests.Session` for persistent connections
- Connection pooling and cookie handling automatic
- Configurable timeout and retry logic
- Base URL: `http://localhost:23119/api/users/000000/`
- User-agent includes library version information

### Logging Configuration
- Uses standard Python `logging` module
- Logger name: `zoteroapi`
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- HTTP request/response logging available in DEBUG mode

## Testing Guidelines

### Test Organization
- Unit tests test individual classes/methods in isolation
- Integration tests test complete workflows
- Mock responses are in `tests/fixtures/`
- Test utilities in `tests/utils/`

### Coverage Requirements
- Minimum 85% code coverage (currently 88%)
- Focus on testing public API methods
- Test error paths and edge cases

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Tests that take longer to run
- `@pytest.mark.network`: Tests requiring network access

## Development Environment Setup

### Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate

# Install development dependencies
pip install -e ".[test,docs]"
```

### IDE Configuration
**VS Code settings (`.vscode/settings.json`):**
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

**PyCharm Configuration:**
- Set Python interpreter to `.venv/bin/python`
- Enable pytest as test runner
- Configure code style to follow PEP 8
- Enable type checking

### Debug Configuration
For debugging ZoteroLocal client with local Zotero server:
1. Ensure Zotero desktop app is running
2. Enable local server in Zotero preferences
3. Use breakpoints in `src/zoteroapi/` files
4. Mock network requests when testing offline

## Development Standards

### Code Style
- Follow PEP 8 formatting (enforced by `black`)
- Use `ruff` for linting and code quality checks
- Use type hints throughout (checked by `mypy`)
- Include comprehensive docstrings with Google style
- Handle errors gracefully with appropriate exceptions

### Documentation
- All public methods must have docstrings
- Include examples in docstrings for complex operations
- Documentation is built with MkDocs and Material theme
- API reference generated from docstrings using mkdocstrings
- Chinese documentation with Material theme localization

### Dependencies
- **Runtime**: `requests>=2.25.0` for HTTP requests
- **Testing**: `pytest>=7.0.0`, `pytest-cov>=4.0.0`, `pytest-mock>=3.10.0`
- **Documentation**: `mkdocs>=1.5.0`, `mkdocs-material>=9.4.0`
- **Code Quality**: `black`, `ruff`, `mypy`
- Python 3.11+ required

## Configuration Files

### pyproject.toml
- Uses `hatchling` build system
- Defines project metadata and dependencies
- Optional dependencies for testing (`[test]`) and documentation (`[docs]`)
- Python 3.11+ requirement enforced

### mkdocs.yml
- Material theme with Chinese localization
- Git revision date plugin for change tracking
- mkdocstrings for API reference generation
- Comprehensive navigation structure
- Search and code highlighting enabled

### tests/conftest.py
- Shared pytest fixtures for all test modules
- Sample data fixtures for items, collections, and notes
- Temporary file management utilities
- Mock API response datasets
- Automatic cleanup after tests

### Git Configuration
- `.gitignore` excludes Python cache, build artifacts, and coverage reports
- Development workflow follows git-flow pattern
- Main branch: `main`, development branch: `dev`

## Zotero Local Server Requirements

- Zotero desktop application must be running
- Local server enabled in Zotero preferences (Advanced → Config Editor → `extensions.zotero.httpServer.enabled = true`)
- Default port: 23119
- Default URL: `http://localhost:23119/api/users/000000/`
- No authentication required for local access
- Restart Zotero after enabling server

## Common Workflows

### Basic Usage Pattern
```python
from zoteroapi import ZoteroLocal
client = ZoteroLocal()
items = client.get_items_top(limit=10)
```

### Error Handling Pattern
```python
from zoteroapi import ZoteroLocalError, ResourceNotFound
try:
    item = client.get_item(item_key)
except ResourceNotFound:
    print("Item not found")
except ZoteroLocalError as e:
    print(f"API Error: {e}")
```

### Search Pattern
```python
# Keyword search
results = client.search_items("machine learning")

# DOI search
results = client.search_by_doi("10.1038/nature12373")

# PMID search
results = client.search_by_pmid("12345678")
```