# ZoteroAPI 测试指南

本文档介绍如何运行 ZoteroAPI 项目的测试套件。

## 测试概述

本项目使用 pytest 作为测试框架，包含：
- **111 个测试用例**
- **88% 的代码覆盖率**（超过 85% 的目标）
- 单元测试和集成测试

## 安装测试依赖

```bash
pip install -e ".[test]"
```

这将安装以下测试依赖：
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- pytest-mock >= 3.10.0
- requests-mock >= 1.9.0
- pytest-xdist >= 3.0.0

## 运行测试

### 运行所有测试

```bash
pytest tests/
```

### 运行单元测试

```bash
pytest tests/unit/
```

### 运行集成测试

```bash
pytest tests/integration/
```

### 运行指定模块的测试

```bash
# 测试基础客户端
pytest tests/unit/test_base_client.py

# 测试异常类
pytest tests/unit/test_exceptions.py

# 测试搜索功能
pytest tests/unit/mixins/test_search.py
```

### 跳过慢速测试

```bash
pytest tests/ -m "not slow"
```

### 详细输出模式

```bash
pytest tests/ -v
```

## 代码覆盖率

### 生成覆盖率报告

```bash
# 终端显示覆盖率
pytest tests/ --cov=src/zoteroapi --cov-report=term

# 生成 HTML 覆盖率报告
pytest tests/ --cov=src/zoteroapi --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html
```

### 当前覆盖率

| 模块 | 覆盖率 |
|------|--------|
| exceptions.py | 100% |
| __init__.py | 100% |
| mixins/notes.py | 100% |
| base_client.py | 94% |
| client.py | 91% |
| mixins/search.py | 91% |
| mixins/files.py | 50% |
| **总计** | **88%** |

## 测试标记

测试使用以下标记进行分类：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.slow` - 慢速测试（涉及文件 I/O）
- `@pytest.mark.network` - 需要网络的测试

### 按标记运行测试

```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"
```

## 并行测试执行

使用 pytest-xdist 并行运行测试：

```bash
pytest tests/ -n auto
```

## 测试目录结构

```
tests/
├── conftest.py                    # 全局 fixtures
├── unit/                          # 单元测试
│   ├── test_base_client.py        # 基础客户端测试
│   ├── test_client.py             # 主客户端测试
│   ├── test_exceptions.py         # 异常类测试
│   └── mixins/                    # Mixin 模块测试
│       ├── test_search.py         # 搜索功能测试
│       ├── test_files.py          # 文件操作测试
│       └── test_notes.py          # 笔记功能测试
├── integration/                   # 集成测试
│   ├── test_workflows.py          # 工作流测试
│   └── test_api_integration.py    # API 集成测试
├── fixtures/                      # 测试数据
│   ├── mock_data.py               # Mock 数据工厂
│   ├── sample_responses.py        # 样本 API 响应
│   └── test_files/                # 测试用文件
└── utils/                         # 测试工具
    └── helpers.py                 # 辅助函数
```

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `pytest` | 运行所有测试 |
| `pytest tests/unit` | 运行单元测试 |
| `pytest tests/integration` | 运行集成测试 |
| `pytest -v` | 详细输出 |
| `pytest -k "test_search"` | 运行名称匹配的测试 |
| `pytest --cov=src/zoteroapi` | 生成覆盖率报告 |
| `pytest -n auto` | 并行运行 |
| `pytest -m "not slow"` | 跳过慢速测试 |
| `pytest --lf` | 只运行上次失败的测试 |
| `pytest --tb=short` | 简短的错误回溯 |

## CI/CD 集成

在持续集成环境中运行测试：

```bash
# 快速测试（跳过慢速测试）
pytest tests/unit -m "not slow" --tb=short

# 完整测试（包含覆盖率）
pytest tests/ --cov=src/zoteroapi --cov-report=xml --cov-fail-under=85
```

## 常见问题

### 测试失败了怎么办？

1. 查看详细错误信息：`pytest -v --tb=long`
2. 运行单个失败的测试：`pytest tests/path/to/test.py::TestClass::test_method`
3. 使用 `--pdb` 进入调试模式：`pytest --pdb`

### 如何添加新测试？

1. 在相应的测试目录创建测试文件（`test_*.py`）
2. 编写测试函数（以 `test_` 开头）
3. 使用 fixtures 提供测试数据
4. 运行测试验证

### 如何模拟 HTTP 请求？

使用 `requests_mock` fixture：

```python
def test_example(requests_mock):
    requests_mock.get(
        "http://localhost:23119/api/users/000000/items/TEST123",
        json={"key": "TEST123"},
        status_code=200
    )
    # 你的测试代码
```

## 贡献指南

在提交代码前，请确保：
1. 所有测试通过：`pytest tests/`
2. 代码覆盖率达到 85% 以上
3. 新功能包含相应的测试用例
4. 遵循项目的代码规范

## 参考资源

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)
- [requests-mock 文档](https://requests-mock.readthedocs.io/)
