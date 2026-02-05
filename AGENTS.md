# AGENTS.md

This file provides guidance for AI agents working on the zoteroapi codebase.

## Build, Lint, and Test Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_client.py

# Run specific test function
pytest tests/unit/test_client.py::TestZoteroLocal::test_get_items_top

# Run tests with coverage
pytest --cov=src/zoteroapi --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests in parallel
pytest -n auto

# Stop on first failure
pytest -x
```

### Code Quality
```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/
black src/ tests/

# Type checking with mypy
mypy src/

# Run all quality checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Package Management
```bash
# Install development dependencies
pip install -e ".[test,docs]"

# Build package
python -m build

# Install in development mode
pip install -e .
```

## Code Style Guidelines

### Imports
Order imports in three groups separated by blank lines:
1. Standard library imports (`os`, `requests`, `typing`, etc.)
2. Third-party imports
3. Local application imports (relative imports with `.` prefix)

```python
import requests
import os
from pathlib import Path
from typing import Dict, List, Optional

from .exceptions import ZoteroLocalError
from .base_client import BaseZoteroClient
from .mixins.search import SearchMixin
```

### Formatting
- Follow PEP 8 (enforced by `black`)
- Line length: 88 characters (black default)
- Use trailing commas for multi-line calls
- Use spaces around operators

### Type Hints
- Use type hints for all function signatures
- Common types: `Dict`, `List`, `Optional`, `Union`
- Use concrete types over `Any` when possible
- Import types from `typing` module

```python
def get_item(self, item_key: str) -> Dict:
def get_items(self, limit: Optional[int] = None) -> List[Dict]:
def upload_file(
    self,
    file_path: Union[str, Path],
    parent_item: Optional[str] = None,
) -> Dict:
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `ZoteroLocal`, `BaseZoteroClient`)
- **Functions/Variables**: `snake_case` (e.g., `get_item`, `file_path`)
- **Private methods**: leading underscore (e.g., `_make_request`)
- **Constants**: `UPPER_SNAKE_CASE`

### Error Handling
- Use custom exceptions from `src/zoteroapi/exceptions.py`
- Base exception: `ZoteroLocalError`
- Specific exceptions: `ConnectionError`, `AuthenticationError`, `ResourceNotFound`
- Wrap external API calls with try/except and raise `ZoteroLocalError`
- Provide meaningful error messages

```python
from .exceptions import ZoteroLocalError, ResourceNotFound

try:
    item = self.get_item(item_key)
except ResourceNotFound:
    raise ZoteroLocalError(f"Item {item_key} not found")
except Exception as e:
    raise ZoteroLocalError(f"Failed to get item: {str(e)}")
```

### Docstrings
- Use Google-style docstrings
- Include: Description, Args, Returns, Raises, Examples
- All public methods must have docstrings

```python
def get_item(self, item_key: str) -> Dict:
    """获取单个文献条目。

    通过条目的唯一标识符获取其完整信息。

    Args:
        item_key: 条目的唯一标识符（key）

    Returns:
        包含完整条目信息的字典

    Raises:
        ZoteroLocalError: 当 API 请求失败时抛出
        ResourceNotFound: 当条目不存在时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> item = client.get_item("ABC123XYZ")
    """
```

### Project Architecture
- **Mixin Pattern**: Add domain-specific functionality to mixins in `src/zoteroapi/mixins/`
- **BaseZoteroClient**: Handles HTTP communication (do not modify unless changing HTTP layer)
- **ZoteroLocal**: Main client class, inherits from BaseZoteroClient and mixins
- **API Responses**: Return raw JSON from API (handled by `_make_request`)

### Zotero API Integration
- Follow Zotero API v3 specification
- All API responses default to JSON format
- Handle pagination where applicable
- Reference: https://www.zotero.org/support/dev/web_api/v3/basics

### File Operations
- Use `pathlib.Path` for path handling
- Ensure proper cross-platform compatibility
- Handle compressed files (ZIP format) from Zotero API
- Use binary mode (`'rb'`, `'wb'`) for file operations

### Testing
- Minimum 85% code coverage
- Use `@pytest.mark.unit` and `@pytest.mark.integration` markers
- Mock API responses in `tests/fixtures/`
- Test error paths and edge cases
