# 贡献指南

感谢您对 ZoteroAPI 项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能

## 开始之前

### 开发环境要求

- **Python**: 3.11+
- **Git**: 用于版本控制
- **Zotero**: 用于测试（需要启用本地服务器）

### 项目结构

```
zoteroapi/
├── src/zoteroapi/           # 源代码
│   ├── __init__.py         # 包初始化
│   ├── client.py           # 主客户端类
│   ├── base_client.py      # 基础客户端
│   ├── exceptions.py       # 异常定义
│   └── mixins/             # 功能混入类
│       ├── search.py       # 搜索功能
│       ├── files.py        # 文件操作
│       └── notes.py        # 笔记管理
├── tests/                  # 测试代码
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── fixtures/          # 测试数据
├── examples/              # 示例代码
├── docs/                  # 文档
├── pyproject.toml         # 项目配置
└── README.md             # 项目说明
```

## 设置开发环境

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/zoteroapi.git
cd zoteroapi
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 使用 conda
conda create -n zoteroapi python=3.11
conda activate zoteroapi
```

### 3. 安装依赖

```bash
# 安装开发依赖
pip install -e ".[test,docs]"

# 或者分别安装
pip install -e .
pip install pytest pytest-cov pytest-mock requests-mock
pip install mkdocs mkdocs-material mkdocstrings
```

### 4. 配置 Zotero

确保 Zotero 桌面应用已安装并配置：

1. 打开 Zotero
2. 进入 **编辑 → 首选项 → 高级**
3. 点击 **配置编辑器**
4. 搜索 `extensions.zotero.httpServer.enabled`
5. 设置为 `true`
6. 重启 Zotero

### 5. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_client.py

# 运行带覆盖率的测试
pytest --cov=src/zoteroapi --cov-report=html
```

## 开发工作流

### 1. 创建分支

```bash
# 从 main 分支创建新分支
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# 或者修复 Bug
git checkout -b fix/bug-description
```

### 2. 编写代码

- 遵循项目的代码风格（见 [代码规范](#代码规范)）
- 添加适当的类型提示
- 编写相应的测试
- 更新相关文档

### 3. 运行测试

```bash
# 运行所有测试确保没有破坏现有功能
pytest

# 运行特定相关的测试
pytest tests/unit/test_search.py

# 检查代码覆盖率
pytest --cov=src/zoteroapi --cov-report=term-missing
```

### 4. 提交更改

```bash
# 添加更改的文件
git add .

# 提交（使用有意义的提交信息）
git commit -m "feat: 添加新的搜索功能

- 实现按作者搜索
- 添加相关测试
- 更新文档"

# 推送到远程分支
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

1. 在 GitHub 上创建 Pull Request
2. 填写 PR 模板
3. 等待代码审查
4. 根据反馈进行修改

## 代码规范

### Python 代码风格

我们使用以下工具和规范：

- **PEP 8**: Python 官方代码风格指南
- **Black**: 代码格式化工具
- **isort**: 导入排序工具
- **flake8**: 代码检查工具
- **mypy**: 类型检查工具

#### 安装开发工具

```bash
pip install black isort flake8 mypy
```

#### 代码格式化

```bash
# 格式化代码
black src/ tests/

# 排序导入
isort src/ tests/

# 检查代码风格
flake8 src/ tests/

# 类型检查
mypy src/
```

#### 代码风格示例

```python
# ✅ 好的示例
from typing import Dict, List, Optional
import requests

from .exceptions import ZoteroLocalError


class ExampleClass:
    """示例类。

    详细描述类的功能和使用方法。

    Attributes:
        attr1: 属性1的描述
        attr2: 属性2的描述
    """

    def __init__(self, param1: str, param2: Optional[int] = None):
        """初始化示例类。

        Args:
            param1: 参数1的描述
            param2: 参数2的描述，可选

        Raises:
            ZoteroLocalError: 当初始化失败时抛出
        """
        self.attr1 = param1
        self.attr2 = param2

    def example_method(self, data: List[Dict]) -> Dict:
        """示例方法。

        详细描述方法的功能和实现逻辑。

        Args:
            data: 输入数据列表

        Returns:
            处理后的结果字典

        Examples:
            >>> obj = ExampleClass("test")
            >>> result = obj.example_method([{"key": "value"}])
            >>> print(result)
        """
        processed_data = {}
        for item in data:
            key = item.get("key")
            if key:
                processed_data[key] = item

        return processed_data


# ❌ 不好的示例
import requests

class exampleClass:  # 类名应该使用 PascalCase
    def __init__(self, param1):  # 缺少类型提示和文档字符串
        self.attr1=param1  # 缺少空格

    def method(self, data):  # 方法名不够描述性
        return data[0]  # 可能导致 IndexError
```

### 文档字符串规范

使用 Google 风格的文档字符串：

```python
def search_items(self, query: str, limit: int = 10) -> List[Dict]:
    """搜索文献条目。

    根据查询关键词搜索文献，支持分页返回结果。

    Args:
        query: 搜索关键词，支持多个词的模糊匹配
        limit: 返回结果的最大数量，默认为10

    Returns:
        包含匹配文献信息的字典列表，每个字典包含：
        - key: 文献唯一标识
        - data: 文献详细信息
        - links: 相关链接

    Raises:
        ZoteroLocalError: 当搜索请求失败时抛出
        ValueError: 当查询参数为空时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> results = client.search_items("machine learning", limit=5)
        >>> print(f"找到 {len(results)} 篇文献")
        >>> for item in results:
        ...     print(item['data']['title'])

    Note:
        搜索不区分大小写
        对于大型文献库，建议使用较小的 limit 值
    """
```

## 测试指南

### 测试结构

```
tests/
├── conftest.py              # pytest 配置和 fixtures
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

### 编写测试

#### 单元测试示例

```python
import pytest
from unittest.mock import Mock, patch

from zoteroapi.client import ZoteroLocal
from zoteroapi.exceptions import ResourceNotFound


class TestZoteroLocal:
    """ZoteroLocal 类的单元测试"""

    def test_get_item_success(self, mock_client_response):
        """测试成功获取文献条目"""
        # Arrange
        client = ZoteroLocal()
        item_key = "TEST12345"
        expected_data = {"key": item_key, "data": {"title": "测试文献"}}

        mock_client_response.json.return_value = expected_data

        # Act
        result = client.get_item(item_key)

        # Assert
        assert result == expected_data

    def test_get_item_not_found(self, mock_client_response):
        """测试获取不存在的文献条目"""
        # Arrange
        client = ZoteroLocal()
        item_key = "INVALID_KEY"

        mock_client_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")

        # Act & Assert
        with pytest.raises(ResourceNotFound):
            client.get_item(item_key)

    @pytest.mark.parametrize("query,expected_count", [
        ("machine learning", 5),
        ("deep learning", 3),
        ("nonexistent", 0)
    ])
    def test_search_items(self, mock_client_response, query, expected_count):
        """测试搜索功能参数化"""
        # Arrange
        client = ZoteroLocal()
        mock_data = [{"key": f"ITEM{i}"} for i in range(expected_count)]
        mock_client_response.json.return_value = mock_data

        # Act
        result = client.search_items(query)

        # Assert
        assert len(result) == expected_count
```

#### 集成测试示例

```python
import pytest
from zoteroapi import ZoteroLocal


@pytest.mark.integration
class TestIntegration:
    """集成测试类"""

    def test_full_workflow(self):
        """测试完整的操作流程"""
        client = ZoteroLocal()

        # 1. 获取文献列表
        items = client.get_items_top(limit=5)
        assert len(items) <= 5

        if items:
            # 2. 获取第一个文献的详细信息
            first_item = items[0]
            item_key = first_item['key']

            detailed_item = client.get_item(item_key)
            assert detailed_item['key'] == item_key

            # 3. 获取文献的笔记
            notes = client.get_item_notes(item_key)
            assert isinstance(notes, list)

            # 4. 添加新笔记
            note_content = "<p>测试笔记内容</p>"
            new_note = client.add_item_note(item_key, note_content)
            assert 'key' in new_note
            assert new_note['data']['note'] == note_content
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_client.py

# 运行特定测试类
pytest tests/unit/test_client.py::TestZoteroLocal

# 运行特定测试方法
pytest tests/unit/test_client.py::TestZoteroLocal::test_get_item_success

# 运行带标记的测试
pytest -m unit          # 只运行单元测试
pytest -m integration   # 只运行集成测试
pytest -m "not slow"    # 排除慢速测试

# 生成覆盖率报告
pytest --cov=src/zoteroapi --cov-report=html

# 并行运行测试
pytest -n auto  # 需要安装 pytest-xdist
```

## 文档贡献

### 文档结构

```
docs/
├── getting-started/     # 快速开始
│   ├── installation.md
│   ├── configuration.md
│   └── quick-start.md
├── user-guide/         # 用户指南
│   ├── client-initialization.md
│   ├── items-management.md
│   ├── collections.md
│   ├── search.md
│   ├── notes.md
│   ├── files.md
│   └── tags.md
├── examples/           # 示例代码
│   ├── basic-usage.md
│   ├── search-examples.md
│   ├── file-operations.md
│   ├── note-operations.md
│   └── advanced-workflows.md
├── api-reference/      # API 参考
│   ├── index.md
│   ├── client.md
│   ├── base-client.md
│   ├── mixins/
│   │   ├── search.md
│   │   ├── files.md
│   │   └── notes.md
│   └── exceptions.md
└── development/        # 开发指南
    ├── contributing.md
    ├── testing.md
    ├── architecture.md
    └── changelog.md
```

### 编写文档

使用 Markdown 格式，遵循以下规范：

```markdown
# 页面标题

简短的页面描述。

## 主要章节

### 子章节

#### 具体内容

- 使用列表说明要点
- 包含代码示例

```python
# 代码示例
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
items = client.get_items_top(limit=10)
```

> **注意**: 重要信息使用引用块

!!! warning "警告"
    警告信息使用警告块
```

### 构建文档

```bash
# 本地预览
mkdocs serve

# 构建静态文件
mkdocs build

# 部署到 GitHub Pages
mkdocs gh-deploy
```

## 提交 Pull Request

### PR 标题规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式化
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: 添加按作者搜索功能
fix: 修复文件下载的内存泄漏问题
docs: 更新 API 参考文档
```

### PR 描述模板

```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 变更描述
简要描述本次变更的内容和原因。

## 测试
- [ ] 单元测试已通过
- [ ] 集成测试已通过
- [ ] 手动测试已完成

## 检查清单
- [ ] 代码符合项目规范
- [ ] 已添加必要的测试
- [ ] 文档已更新
- [ ] 提交信息符合规范
```

## 发布流程

### 版本号规范

使用 [Semantic Versioning](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- `1.0.0`: 主要版本（不兼容的 API 变更）
- `0.1.0`: 次要版本（向后兼容的功能新增）
- `0.0.1`: 补丁版本（向后兼容的问题修正）

### 发布步骤

1. 更新版本号：
   ```bash
   # 更新 __init__.py 中的版本号
   # 更新 pyproject.toml 中的版本号
   ```

2. 更新 CHANGELOG.md

3. 创建发布标签：
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

4. 构建 and 发布：
   ```bash
   python -m build
   twine upload dist/*
   ```

## 社区

### 获取帮助

- 📖 [文档](https://yourusername.github.io/zoteroapi/)
- 🐛 [Issues](https://github.com/yourusername/zoteroapi/issues)
- 💬 [Discussions](https://github.com/yourusername/zoteroapi/discussions)

### 行为准则

我们致力于为每个人提供友好、安全和欢迎的环境。请遵循我们的行为准则：

- 尊重不同的观点和经验
- 使用友好和包容的语言
- 接受建设性的批评
- 关注对社区最有利的事情

## 致谢

感谢所有为 ZoteroAPI 项目做出贡献的开发者！

您的贡献将被记录在 [CONTRIBUTORS.md](CONTRIBUTORS.md) 文件中。

---

再次感谢您的贡献！🎉