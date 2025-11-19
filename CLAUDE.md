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

# Run specific test file
pytest tests/unit/test_client.py

# Run tests with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests with specific markers
pytest -m "unit"
pytest -m "integration"
pytest -m "slow"
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

### Package Management
```bash
# Install development dependencies
pip install -e ".[test,docs]"

# Build package
python -m build

# Install package
pip install -e .
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

## Development Standards

### Code Style
- Follow PEP 8 formatting
- Use type hints throughout
- Include comprehensive docstrings with Google style
- Handle errors gracefully with appropriate exceptions

### Documentation
- All public methods must have docstrings
- Include examples in docstrings for complex operations
- Documentation is built with MkDocs and Material theme
- API reference generated from docstrings using mkdocstrings

### Dependencies
- `requests>=2.25.0` for HTTP requests
- `pytest>=7.0.0` for testing
- `mkdocs>=1.5.0` for documentation
- Python 3.11+ required

## Zotero Local Server Requirements

- Zotero desktop application must be running
- Local server enabled in Zotero preferences
- Default port: 23119
- No authentication required for local access

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