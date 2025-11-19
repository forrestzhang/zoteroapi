# API 参考概览

本文档提供了 ZoteroAPI 的完整 API 参考，包括所有类、方法和函数的详细说明。

## 核心组件

### 主要类

- **[ZoteroLocal](client.md)** - 主要客户端类，继承自 BaseZoteroClient 和所有 Mixin 类
- **[BaseZoteroClient](base-client.md)** - 基础 HTTP 客户端类，处理请求和响应

### Mixin 类

- **[SearchMixin](mixins/search.md)** - 搜索功能相关方法
- **[FilesMixin](mixins/files.md)** - 文件操作相关方法
- **[NotesMixin](mixins/notes.md)** - 笔记管理相关方法

### 异常类

- **[异常类](exceptions.md)** - 所有自定义异常的详细说明

## API 设计原则

### 一致的接口设计

所有 API 方法都遵循以下设计原则：

1. **返回值类型一致** - 大多数方法返回字典或列表
2. **错误处理统一** - 所有方法抛出 `ZoteroLocalError` 或其子类
3. **参数命名规范** - 使用描述性的参数名
4. **文档完整性** - 所有公共方法都有详细的 docstring

### RESTful API 映射

ZoteroAPI 方法直接映射到 Zotero REST API v3 端点：

```python
# Zotero REST API: GET /items
# ZoteroAPI: client.get_items()

# Zotero REST API: GET /items/{itemKey}
# ZoteroAPI: client.get_item(item_key)

# Zotero REST API: GET /collections
# ZoteroAPI: client.get_collections()
```

## 基础用法模式

### 客户端初始化

```python
from zoteroapi import ZoteroLocal

# 使用默认配置
client = ZoteroLocal()

# 使用自定义 URL
client = ZoteroLocal(base_url="http://localhost:23120/api/users/000000/")
```

### 错误处理

```python
from zoteroapi import ZoteroLocalError, ResourceNotFound

try:
    item = client.get_item("INVALID_KEY")
except ResourceNotFound:
    print("条目不存在")
except ZoteroLocalError as e:
    print(f"API 错误: {e}")
```

### 响应数据结构

ZoteroAPI 返回的数据结构与 Zotero API v3 保持一致：

```python
{
    "key": "ABC123XYZ",
    "version": 123,
    "library": {
        "type": "user",
        "id": 12345,
        "name": "My Library"
    },
    "links": {
        "self": {...},
        "alternate": {...}
    },
    "meta": {...},
    "data": {
        "key": "ABC123XYZ",
        "version": 123,
        "itemType": "journalArticle",
        "title": "论文标题",
        "creators": [...],
        "tags": [...],
        # ... 其他字段
    }
}
```

## 搜索和筛选

### 内置搜索方法

```python
# 关键词搜索
results = client.search_items("machine learning")

# DOI 搜索
results = client.search_by_doi("10.1038/nature12373")

# PMID 搜索
results = client.search_by_pmid("12345678")

# 标题搜索
results = client.search_by_title("deep learning", exact_match=False)
```

### 自定义筛选

```python
# 获取顶层文献
top_items = client.get_items_top(limit=10)

# 获取文献集中的文献
collection_items = client.get_collection_items(collection_key)

# 按标签筛选（需要自定义实现）
tagged_items = filter_by_tag(all_items, "machine_learning")
```

## 数据操作模式

### 读取操作

```python
# 获取单个条目
item = client.get_item(item_key)

# 获取列表
items = client.get_items(limit=50)

# 获取集合
collections = client.get_collections()
```

### 写入操作

```python
# 添加笔记
note = client.add_item_note(item_key, "笔记内容")

# 上传文件（需要相应的方法）
# attachment = client.upload_file(file_path, parent_item_key)
```

## 性能考虑

### 连接复用

`BaseZoteroClient` 使用 `requests.Session` 自动复用 HTTP 连接：

```python
client = ZoteroLocal()
# 所有请求共享同一个会话
for i in range(100):
    items = client.get_items_top(limit=10)
```

### 分页处理

对于大型文献库，建议使用 `limit` 参数进行分页：

```python
# 不推荐 - 可能导致内存问题
all_items = client.get_items()

# 推荐 - 分页处理
batch_size = 100
page = 0
while True:
    items = client.get_items(limit=batch_size)  # 需要实现 offset 参数
    if not items:
        break
    # 处理当前页
    process_items(items)
    page += 1
```

### 缓存策略

客户端实现了基础缓存机制：

```python
client = ZoteroLocal()
# 第一次请求会访问 API
items1 = client.get_items_top(limit=10)

# 相同请求可能从缓存返回（取决于实现）
items2 = client.get_items_top(limit=10)
```

## 扩展和自定义

### 添加自定义方法

```python
class CustomZoteroClient(ZoteroLocal):
    """自定义客户端，添加额外功能"""

    def get_items_by_author(self, author_name):
        """按作者获取文献"""
        all_items = self.get_items()
        return [
            item for item in all_items
            if self._has_author(item, author_name)
        ]

    def _has_author(self, item, author_name):
        """检查文献是否包含指定作者"""
        creators = item.get('data', {}).get('creators', [])
        return any(
            creator.get('lastName', '').lower() == author_name.lower()
            for creator in creators
            if creator.get('creatorType') == 'author'
        )
```

### 自定义异常处理

```python
from zoteroapi import ZoteroLocalError

class CustomErrorHandler:
    """自定义错误处理器"""

    def __init__(self, client):
        self.client = client

    def safe_get_item(self, item_key, default=None):
        """安全获取条目，返回默认值而不是抛出异常"""
        try:
            return self.client.get_item(item_key)
        except ZoteroLocalError:
            return default
```

## 版本兼容性

### Zotero API 版本

ZoteroAPI 与 Zotero API v3 兼容：

- 支持所有标准的端点和方法
- 遵循 API 响应格式规范
- 处理标准 HTTP 状态码

### Python 版本

- 最低要求：Python 3.11+
- 推荐版本：Python 3.11+ 最新稳定版
- 已测试平台：Windows, macOS, Linux

## 故障排除

### 常见问题

1. **连接错误**
   ```python
   # 确保 Zotero 正在运行
   # 检查本地服务器是否启用
   # 验证端口配置
   ```

2. **权限错误**
   ```python
   # 检查文件系统权限
   # 验证下载目录可写
   ```

3. **数据格式错误**
   ```python
   # 验证 API 响应格式
   # 检查数据类型匹配
   ```

### 调试技巧

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 使用调试模式
client = ZoteroLocal()
client.debug = True  # 如果支持
```

## 最佳实践

### 资源管理

```python
# 推荐：使用 with 语句（如果支持）
with ZoteroLocal() as client:
    items = client.get_items()

# 当前：手动管理
client = ZoteroLocal()
try:
    items = client.get_items()
finally:
    # 清理资源（如果需要）
    pass
```

### 错误恢复

```python
def robust_api_call(func, *args, max_retries=3, **kwargs):
    """带重试机制的 API 调用"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ZoteroLocalError as e:
            if attempt == max_retries - 1:
                raise
            print(f"尝试 {attempt + 1} 失败，重试中...")
            time.sleep(2 ** attempt)  # 指数退避

# 使用
item = robust_api_call(client.get_item, item_key)
```

这些模式和实践可以帮助你更有效地使用 ZoteroAPI。