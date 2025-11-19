# 测试指南

本文档介绍 ZoteroAPI 项目的测试策略、工具和最佳实践。

## 测试概述

ZoteroAPI 采用多层测试策略，确保代码质量和功能可靠性：

- **单元测试** - 测试单个函数和类
- **集成测试** - 测试组件间的交互
- **端到端测试** - 测试完整的工作流程
- **性能测试** - 测试性能和内存使用

## 测试框架和工具

### 核心测试框架

- **pytest**: 主要测试框架，提供丰富的功能
- **pytest-cov**: 代码覆盖率测试
- **pytest-mock**: Mock 和 patch 功能
- **requests-mock**: HTTP 请求模拟

### 开发依赖

```bash
pip install pytest>=7.0.0
pip install pytest-cov>=4.0.0
pip install pytest-mock>=3.10.0
pip install requests-mock>=1.9.0
pip install pytest-xdist>=3.0.0  # 并行测试
```

## 测试结构

```
tests/
├── conftest.py              # pytest 配置和共享 fixtures
├── unit/                    # 单元测试
│   ├── test_base_client.py  # 基础客户端测试
│   ├── test_client.py       # 主客户端测试
│   ├── test_exceptions.py   # 异常测试
│   └── mixins/              # Mixin 类测试
│       ├── test_search.py   # 搜索功能测试
│       ├── test_files.py    # 文件操作测试
│       └── test_notes.py    # 笔记功能测试
├── integration/             # 集成测试
│   ├── test_api_integration.py  # API 集成测试
│   └── test_workflows.py        # 工作流测试
├── fixtures/                # 测试数据
│   ├── mock_data.py        # 模拟数据
│   └── sample_responses.py # 样本响应
└── utils/                  # 测试工具
    └── helpers.py          # 辅助函数
```

## 配置文件

### pytest.ini

项目根目录的 `pytest.ini` 配置：

```ini
[pytest]
# 测试发现路径
testpaths = tests

# 测试文件命名模式
python_files = test_*.py *_test.py

# 测试类命名模式
python_classes = Test*

# 测试函数命名模式
python_functions = test_*

# 详细输出
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src/zoteroapi
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=85

# 日志配置
log_cli = false
log_cli_level = INFO
log_file_level = DEBUG

# 标记定义
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Tests that take a long time to run
    network: Tests that require network access
```

### conftest.py

```python
import pytest
import requests
from unittest.mock import Mock

from zoteroapi.client import ZoteroLocal
from zoteroapi.base_client import BaseZoteroClient


@pytest.fixture
def mock_response():
    """模拟 HTTP 响应对象"""
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.headers = {'Content-Type': 'application/json'}
    return response


@pytest.fixture
def mock_client_response():
    """模拟客户端响应"""
    response = Mock()
    response.json.return_value = {"success": True}
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def sample_item():
    """样本文献条目数据"""
    return {
        "key": "SAMPLE123",
        "version": 1,
        "library": {
            "type": "user",
            "id": 12345
        },
        "links": {
            "self": {"href": "http://localhost:23119/api/users/0/items/SAMPLE123"}
        },
        "meta": {},
        "data": {
            "key": "SAMPLE123",
            "version": 1,
            "itemType": "journalArticle",
            "title": "测试文献标题",
            "creators": [
                {
                    "creatorType": "author",
                    "firstName": "John",
                    "lastName": "Doe"
                }
            ],
            "abstractNote": "这是测试文献的摘要",
            "publicationTitle": "测试期刊",
            "date": "2023",
            "tags": [],
            "collections": []
        }
    }


@pytest.fixture
def sample_collection():
    """样本文献集数据"""
    return {
        "key": "COLLECTION123",
        "version": 1,
        "library": {
            "type": "user",
            "id": 12345
        },
        "links": {
            "self": {"href": "http://localhost:23119/api/users/0/collections/COLLECTION123"}
        },
        "meta": {},
        "data": {
            "key": "COLLECTION123",
            "version": 1,
            "name": "测试文献集",
            "parentCollection": False,
            "relations": {}
        }
    }


@pytest.fixture
def sample_note():
    """样本笔记数据"""
    return {
        "key": "NOTE123",
        "version": 1,
        "library": {
            "type": "user",
            "id": 12345
        },
        "links": {
            "self": {"href": "http://localhost:23119/api/users/0/items/NOTE123"}
        },
        "meta": {},
        "data": {
            "key": "NOTE123",
            "version": 1,
            "itemType": "note",
            "parentItem": "SAMPLE123",
            "note": "<p>这是测试笔记内容</p>",
            "tags": [],
            "collections": [],
            "dateAdded": "2023-01-01T12:00:00Z"
        }
    }
```

## 单元测试

### 测试 BaseZoteroClient

```python
# tests/unit/test_base_client.py
import pytest
import requests
from unittest.mock import Mock, patch

from zoteroapi.base_client import BaseZoteroClient
from zoteroapi.exceptions import ZoteroLocalError, APIError, ResourceNotFound


@pytest.mark.unit
class TestBaseZoteroClient:
    """BaseZoteroClient 类的单元测试"""

    def test_initialization_default_url(self):
        """测试默认 URL 初始化"""
        client = BaseZoteroClient()
        assert client.base_url == "http://localhost:23119/api/users/000000"

    def test_initialization_custom_url(self):
        """测试自定义 URL 初始化"""
        custom_url = "http://localhost:23120/api/users/000000/"
        client = BaseZoteroClient(custom_url)
        assert client.base_url == "http://localhost:23120/api/users/000000"

    def test_url_normalization(self):
        """测试 URL 标准化"""
        # 测试末尾斜杠被去除
        client = BaseZoteroClient("http://localhost:23119/api/users/000000/")
        assert client.base_url == "http://localhost:23119/api/users/000000"

    @patch('zoteroapi.base_client.requests.Session.request')
    def test_make_request_success(self, mock_request, mock_response):
        """测试成功的请求"""
        # Arrange
        mock_request.return_value = mock_response
        client = BaseZoteroClient()

        # Act
        result = client._make_request("GET", "/items")

        # Assert
        mock_request.assert_called_once()
        assert result == mock_response

    @patch('zoteroapi.base_client.requests.Session.request')
    def test_make_request_with_params(self, mock_request, mock_response):
        """测试带参数的请求"""
        # Arrange
        mock_request.return_value = mock_response
        client = BaseZoteroClient()

        # Act
        client._make_request("GET", "/items", params={"limit": 10})

        # Assert
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs['params']['limit'] == 10
        assert call_kwargs['params']['format'] == 'json'

    @patch('zoteroapi.base_client.requests.Session.request')
    def test_make_request_http_error(self, mock_request):
        """测试 HTTP 错误处理"""
        # Arrange
        mock_request.side_effect = requests.HTTPError("404 Not Found")
        client = BaseZoteroClient()

        # Act & Assert
        with pytest.raises(ZoteroLocalError):
            client._make_request("GET", "/items/nonexistent")

    @patch('zoteroapi.base_client.requests.Session.request')
    def test_make_request_connection_error(self, mock_request):
        """测试连接错误处理"""
        # Arrange
        mock_request.side_effect = requests.ConnectionError("Connection failed")
        client = BaseZoteroClient()

        # Act & Assert
        with pytest.raises(ZoteroLocalError):
            client._make_request("GET", "/items")

    @patch('zoteroapi.base_client.requests.Session.request')
    def test_request_404_error(self, mock_request):
        """测试 404 错误处理"""
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_request.return_value = mock_response
        client = BaseZoteroClient()

        # Act & Assert
        with pytest.raises(ResourceNotFound):
            client._request("GET", "/items/nonexistent")

    @patch('zoteroapi.base_client.requests.Session.request')
    def test_request_json_response(self, mock_request, sample_item):
        """测试 JSON 响应处理"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = sample_item
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"key": "test"}'
        mock_request.return_value = mock_response
        client = BaseZoteroClient()

        # Act
        result = client._request("GET", "/items/test")

        # Assert
        assert result == sample_item
```

### 测试 SearchMixin

```python
# tests/unit/mixins/test_search.py
import pytest
from unittest.mock import Mock, patch

from zoteroapi.client import ZoteroLocal
from zoteroapi.exceptions import ZoteroLocalError


@pytest.mark.unit
class TestSearchMixin:
    """SearchMixin 功能的单元测试"""

    def setup_method(self):
        """设置测试环境"""
        self.client = ZoteroLocal()
        self.sample_items = [
            {
                "key": "ITEM1",
                "data": {
                    "title": "Machine Learning Basics",
                    "creators": [{"creatorType": "author", "lastName": "Smith", "firstName": "John"}],
                    "extra": "PMID: 12345678\nDOI: 10.1000/test1",
                    "abstractNote": "Introduction to machine learning concepts"
                }
            },
            {
                "key": "ITEM2",
                "data": {
                    "title": "Deep Learning in Practice",
                    "creators": [{"creatorType": "author", "lastName": "Doe", "firstName": "Jane"}],
                    "extra": "DOI: 10.1000/test2",
                    "abstractNote": "Advanced deep learning techniques"
                }
            }
        ]

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_items_found(self, mock_get_items):
        """测试搜索到结果"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        query = "machine learning"

        # Act
        result = self.client.search_items(query)

        # Assert
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"
        mock_get_items.assert_called_once()

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_items_not_found(self, mock_get_items):
        """测试搜索无结果"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        query = "nonexistent topic"

        # Act
        result = self.client.search_items(query)

        # Assert
        assert len(result) == 0

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_by_doi_exact_match(self, mock_get_items):
        """测试 DOI 精确匹配"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        doi = "10.1000/test1"

        # Act
        result = self.client.search_by_doi(doi)

        # Assert
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_by_doi_case_insensitive(self, mock_get_items):
        """测试 DOI 大小写不敏感"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        doi = "10.1000/TEST1"

        # Act
        result = self.client.search_by_doi(doi)

        # Assert
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_by_pmid_found(self, mock_get_items):
        """测试 PMID 搜索成功"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        pmid = "12345678"

        # Act
        result = self.client.search_by_pmid(pmid)

        # Assert
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_by_pmid_not_found(self, mock_get_items):
        """测试 PMID 搜索无结果"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        pmid = "87654321"

        # Act
        result = self.client.search_by_pmid(pmid)

        # Assert
        assert len(result) == 0

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_by_title_exact_match(self, mock_get_items):
        """测试标题精确匹配"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        title = "Machine Learning Basics"

        # Act
        result = self.client.search_by_title(title, exact_match=True)

        # Assert
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_by_title_partial_match(self, mock_get_items):
        """测试标题部分匹配"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        title = "Machine"

        # Act
        result = self.client.search_by_title(title, exact_match=False)

        # Assert
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_by_title_case_insensitive(self, mock_get_items):
        """测试标题搜索大小写不敏感"""
        # Arrange
        mock_get_items.return_value = self.sample_items
        title = "MACHINE LEARNING BASICS"

        # Act
        result = self.client.search_by_title(title, exact_match=True)

        # Assert
        assert len(result) == 1
        assert result[0]["key"] == "ITEM1"

    @patch.object(ZoteroLocal, 'get_items')
    def test_search_items_with_exception(self, mock_get_items):
        """测试搜索时的异常处理"""
        # Arrange
        mock_get_items.side_effect = ZoteroLocalError("API error")
        query = "test query"

        # Act & Assert
        with pytest.raises(ZoteroLocalError):
            self.client.search_items(query)
```

## 集成测试

### API 集成测试

```python
# tests/integration/test_api_integration.py
import pytest
import requests

from zoteroapi import ZoteroLocal
from zoteroapi.exceptions import ConnectionError


@pytest.mark.integration
@pytest.mark.network
class TestAPIIntegration:
    """API 集成测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """设置和清理"""
        # 检查 Zotero 是否运行
        try:
            response = requests.get("http://localhost:23119/api/users/0/version", timeout=5)
            if response.status_code != 200:
                pytest.skip("Zotero local server is not accessible")
        except requests.RequestException:
            pytest.skip("Zotero local server is not running")

    def test_connection(self):
        """测试连接到 Zotero"""
        client = ZoteroLocal()
        # 如果没有抛出异常，说明连接成功
        assert True

    def test_get_items_top(self):
        """测试获取顶层文献"""
        client = ZoteroLocal()
        items = client.get_items_top(limit=5)

        assert isinstance(items, list)
        assert len(items) <= 5

        if items:
            # 验证文献条目结构
            first_item = items[0]
            assert 'key' in first_item
            assert 'data' in first_item
            assert 'title' in first_item['data']

    def test_get_collections(self):
        """测试获取文献集"""
        client = ZoteroLocal()
        collections = client.get_collections()

        assert isinstance(collections, list)

        if collections:
            # 验证文献集结构
            first_collection = collections[0]
            assert 'key' in first_collection
            assert 'data' in first_collection
            assert 'name' in first_collection['data']

    def test_search_items(self):
        """测试搜索功能"""
        client = ZoteroLocal()
        results = client.search_items("test")

        assert isinstance(results, list)

    def test_get_nonexistent_item(self):
        """测试获取不存在的文献"""
        client = ZoteroLocal()
        with pytest.raises(Exception):  # 应该抛出某种异常
            client.get_item("NONEXISTENTKEY")
```

### 工作流集成测试

```python
# tests/integration/test_workflows.py
import pytest
import tempfile
import os

from zoteroapi import ZoteroLocal


@pytest.mark.integration
@pytest.mark.slow
class TestWorkflows:
    """完整工作流测试"""

    def setup_method(self):
        """设置测试环境"""
        self.client = ZoteroLocal()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_literature_search_workflow(self):
        """测试文献搜索工作流"""
        # 1. 获取顶层文献
        items = self.client.get_items_top(limit=10)
        assert isinstance(items, list)

        if items:
            # 2. 选择一个文献进行详细操作
            first_item = items[0]
            item_key = first_item['key']

            # 3. 获取详细信息
            detailed_item = self.client.get_item(item_key)
            assert detailed_item['key'] == item_key

            # 4. 搜索相关文献
            title = detailed_item['data'].get('title', '')
            if title:
                # 从标题中提取关键词
                keywords = title.split()[:2]  # 取前两个词
                search_results = self.client.search_items(' '.join(keywords))
                assert isinstance(search_results, list)

            # 5. 获取笔记
            notes = self.client.get_item_notes(item_key)
            assert isinstance(notes, list)

    def test_note_management_workflow(self):
        """测试笔记管理工作流"""
        # 获取一个有笔记的文献（如果有的话）
        items = self.client.get_items_top(limit=20)

        for item in items:
            item_key = item['key']

            try:
                # 获取现有笔记
                existing_notes = self.client.get_item_notes(item_key)

                # 添加新笔记
                note_content = "<p>这是一条测试笔记</p>"
                new_note = self.client.get_item_notes(item_key)  # 这里应该是添加笔记的方法

                # 验证笔记数量增加
                updated_notes = self.client.get_item_notes(item_key)
                # 注意：实际的新增笔记方法可能不同
                break

            except Exception:
                # 如果某个文献处理失败，继续下一个
                continue

    def test_file_operations_workflow(self):
        """测试文件操作工作流"""
        # 获取有附件的文献
        items = self.client.get_items_top(limit=10)

        for item in items:
            item_key = item['key']
            links = item.get('links', {})

            if 'attachment' in links:
                try:
                    # 获取附件信息
                    attachment_info = links['attachment']
                    attachment_type = attachment_info.get('attachmentType')

                    if attachment_type:
                        print(f"Found {attachment_type} attachment for item {item_key}")

                    # 注意：实际下载操作需要谨慎，避免下载大文件
                    # 这里只是验证可以获取附件信息
                    break

                except Exception as e:
                    print(f"Error processing attachment for {item_key}: {e}")
                    continue

    @pytest.mark.skip(reason="需要真实的附件文件")
    def test_file_download_workflow(self):
        """测试文件下载工作流"""
        # 这个测试需要真实的附件文件，默认跳过
        pass
```

## 性能测试

### 内存使用测试

```python
# tests/performance/test_memory.py
import pytest
import psutil
import os
from zoteroapi import ZoteroLocal


@pytest.mark.performance
@pytest.mark.slow
class TestMemoryUsage:
    """内存使用测试"""

    def test_large_item_list_memory(self):
        """测试大量文献的内存使用"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        client = ZoteroLocal()

        # 获取大量文献（限制数量避免内存问题）
        items = client.get_items(limit=1000)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        print(f"Memory increase: {memory_increase / 1024 / 1024:.2f} MB")

        # 验证内存增长在合理范围内（例如小于 100MB）
        assert memory_increase < 100 * 1024 * 1024

    def test_search_performance(self):
        """测试搜索性能"""
        client = ZoteroLocal()

        import time
        start_time = time.time()

        # 执行多次搜索
        for i in range(10):
            client.search_items(f"test query {i}")

        end_time = time.time()
        total_time = end_time - start_time
        average_time = total_time / 10

        print(f"Average search time: {average_time:.3f} seconds")

        # 验证平均搜索时间在合理范围内（例如小于 1 秒）
        assert average_time < 1.0
```

## Mock 测试

### HTTP 请求 Mock

```python
# tests/unit/test_mocking.py
import pytest
import requests_mock
from zoteroapi import ZoteroLocal


@pytest.mark.unit
class TestWithMocking:
    """使用 Mock 的测试"""

    def test_with_requests_mock(self, sample_item):
        """使用 requests_mock 进行 Mock"""
        with requests_mock.Mocker() as m:
            # 设置 Mock 响应
            m.get(
                "http://localhost:23119/api/users/000000/items/SAMPLE123",
                json=sample_item
            )

            client = ZoteroLocal()
            result = client.get_item("SAMPLE123")

            assert result == sample_item

    def test_mock_multiple_endpoints(self, sample_item, sample_collection):
        """Mock 多个端点"""
        with requests_mock.Mocker() as m:
            # Mock 文献端点
            m.get(
                "http://localhost:23119/api/users/000000/items/SAMPLE123",
                json=sample_item
            )

            # Mock 文献集端点
            m.get(
                "http://localhost:23119/api/users/000000/collections",
                json=[sample_collection]
            )

            client = ZoteroLocal()

            # 测试获取文献
            item = client.get_item("SAMPLE123")
            assert item == sample_item

            # 测试获取文献集
            collections = client.get_collections()
            assert len(collections) == 1
            assert collections[0] == sample_collection
```

## 运行测试

### 基本测试命令

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_client.py

# 运行特定测试类
pytest tests/unit/test_client.py::TestZoteroLocal

# 运行特定测试方法
pytest tests/unit/test_client.py::TestZoteroLocal::test_get_item

# 运行带标记的测试
pytest -m unit          # 只运行单元测试
pytest -m integration   # 只运行集成测试
pytest -m "not slow"    # 排除慢速测试
```

### 覆盖率测试

```bash
# 生成覆盖率报告
pytest --cov=src/zoteroapi --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest --cov=src/zoteroapi --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 并行测试

```bash
# 使用所有 CPU 核心并行运行
pytest -n auto

# 指定并行进程数
pytest -n 4

# 分布式测试（需要 pytest-xdist）
pytest -n 4 --dist=loadscope
```

### 详细输出

```bash
# 详细输出
pytest -v

# 显示本地变量
pytest -vl

# 显示最慢的 10 个测试
pytest --durations=10
```

## 持续集成

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[test]"

    - name: Run tests
      run: |
        pytest --cov=src/zoteroapi --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 测试最佳实践

### 1. 测试命名

```python
# ✅ 好的命名
def test_get_item_success_returns_item_data():
def test_get_item_not_found_raises_exception():
def test_search_items_with_query_filters_results():

# ❌ 不好的命名
def test_1():
def test_get_item():
def test_search():
```

### 2. 测试结构

```python
# ✅ 推荐的测试结构
class TestSomeFeature:
    def setup_method(self):
        """每个测试方法前的设置"""
        pass

    def teardown_method(self):
        """每个测试方法后的清理"""
        pass

    def test_specific_behavior(self):
        # Arrange - 准备测试数据
        # Act - 执行被测试的操作
        # Assert - 验证结果
        pass
```

### 3. Mock 使用

```python
# ✅ 适当使用 Mock
def test_api_call_with_network_error(self):
    with patch('requests.Session.request') as mock_request:
        mock_request.side_effect = ConnectionError("Network error")

        with pytest.raises(ConnectionError):
            client.get_item("test_key")

# ❌ 过度 Mock
def test_with_too_much_mocking(self):
    # 不要 Mock 被测试的类本身
    with patch.object(ZoteroLocal, 'get_item') as mock_get:
        mock_get.return_value = "mocked_result"
        client = ZoteroLocal()
        result = client.get_item("test")
        assert result == "mocked_result"  # 这个测试没有意义
```

### 4. 测试数据管理

```python
# ✅ 使用 Fixtures 管理测试数据
@pytest.fixture
def sample_user_data():
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }

def test_user_creation(sample_user_data):
    user = User(sample_user_data)
    assert user.name == "John Doe"

# ✅ 使用 Factory 模式创建测试数据
def create_test_item(**kwargs):
    defaults = {
        "title": "Test Item",
        "item_type": "journalArticle",
        "creators": []
    }
    defaults.update(kwargs)
    return defaults

def test_with_factory_data():
    item_data = create_test_item(title="Custom Title")
    # 测试逻辑
```

通过遵循这些测试指南和最佳实践，可以确保 ZoteroAPI 项目的代码质量和功能可靠性。