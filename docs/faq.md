# 常见问题

本文档收集了 ZoteroAPI 使用过程中的常见问题和解决方案。

## 安装和配置

### Q: 如何安装 ZoteroAPI？

**A:** 使用 pip 安装：

```bash
pip install zoteroapi
```

或者从源码安装：

```bash
git clone https://github.com/yourusername/zoteroapi.git
cd zoteroapi
pip install -e .
```

### Q: 支持哪些 Python 版本？

**A:** ZoteroAPI 需要 Python 3.11 或更高版本。

### Q: 如何配置 Zotero 本地服务器？

**A:** 按以下步骤配置：

1. 打开 Zotero 桌面应用
2. 进入 **编辑 → 首选项 → 高级**
3. 点击 **配置编辑器**
4. 搜索 `extensions.zotero.httpServer.enabled`
5. 将其值设置为 `true`
6. 重启 Zotero

### Q: 如何验证 Zotero 本地服务器是否工作？

**A:** 在浏览器中访问：
```
http://localhost:23119/api/users/0/version
```

如果看到版本信息，说明服务器正常工作。

### Q: 默认端口 23119 被占用怎么办？

**A:** 可以在 Zotero 配置中修改端口：

1. 打开配置编辑器
2. 搜索 `extensions.zotero.httpServer.port`
3. 设置为您想要的端口号
4. 在代码中使用自定义 URL：
   ```python
   client = ZoteroLocal(base_url="http://localhost:23120/api/users/000000/")
   ```

## 基础使用

### Q: 如何获取所有文献？

**A:** 使用 `get_items()` 方法：

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
items = client.get_items()  # 获取所有文献（可能很慢）
top_items = client.get_items_top(limit=10)  # 只获取顶层文献，推荐
```

### Q: 如何获取特定文献？

**A:** 使用文献的 key：

```python
item = client.get_item("ITEM_KEY_HERE")
title = item['data']['title']
```

### Q: 如何搜索文献？

**A:** ZoteroAPI 提供多种搜索方式：

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

### Q: 如何获取文献集？

**A:** 使用集合相关方法：

```python
# 获取所有文献集
collections = client.get_collections()

# 获取特定文献集
collection = client.get_collection("COLLECTION_KEY")

# 获取文献集中的文献
items = client.get_collection_items("COLLECTION_KEY")
```

## 文件操作

### Q: 如何下载附件文件？

**A:** 使用以下方法：

```python
# 获取文件内容
file_content = client.get_item_file("ITEM_KEY")

# 下载到指定路径
client.download_file("ITEM_KEY", "./paper.pdf")

# 复制到下载目录
dest_path = client.copy_attachment_to_downloads("file_uri")
```

### Q: 如何上传文件作为附件？

**A:** 使用 `upload_file()` 方法：

```python
result = client.upload_file(
    "/path/to/file.pdf",
    parent_item="PARENT_ITEM_KEY",
    title="研究论文"
)
```

### Q: 下载文件时出现内存错误怎么办？

**A:** 对于大文件，建议使用流式下载：

```python
# 使用 generator 处理大文件
def download_large_file(client, item_key, chunk_size=8192):
    response = client._session.get(
        f"{client.base_url}/items/{item_key}/file",
        stream=True,
        params={"format": "raw"}
    )

    with open("large_file.pdf", "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
```

### Q: 如何处理文件路径问题？

**A:** ZoteroAPI 会自动处理跨平台路径，但建议使用 `pathlib`：

```python
from pathlib import Path

# 使用 Path 对象
file_path = Path("/path/to/file.pdf")
client.upload_file(file_path)
```

## 笔记管理

### Q: 如何获取文献的所有笔记？

**A:** 使用 `get_item_notes()` 方法：

```python
notes = client.get_item_notes("ITEM_KEY")
for note in notes:
    content = note['data']['note']
    print(f"笔记内容: {content}")
```

### Q: 如何添加新笔记？

**A:** 使用 `add_item_note()` 方法：

```python
# 简单笔记
note = client.add_item_note(
    "ITEM_KEY",
    "<p>这是我的笔记内容</p>"
)

# 带标题的格式化笔记
html_content = """
<h2>研究要点</h2>
<ul>
    <li>重要发现1</li>
    <li>重要发现2</li>
</ul>
"""
note = client.add_item_note(
    "ITEM_KEY",
    html_content,
    title="研究要点"
)
```

### Q: 笔记内容为什么是 HTML 格式？

**A:** Zotero 使用 HTML 格式存储笔记，支持富文本格式：

```python
# 支持的 HTML 标签
html_note = """
<h2>标题</h2>
<p>段落文本</p>
<ul>
    <li>列表项1</li>
    <li>列表项2</li>
</ul>
<strong>粗体文本</strong>
<em>斜体文本</em>
"""
```

### Q: 如何将纯文本转换为 HTML？

**A:** 简单的转换方法：

```python
def text_to_html(text):
    """将纯文本转换为基本 HTML"""
    import html
    # 转义 HTML 特殊字符
    escaped = html.escape(text)
    # 将换行符转换为 <p> 标签
    paragraphs = escaped.split('\n\n')
    return ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
```

## 搜索功能

### Q: 搜索功能不区分大小写吗？

**A:** 是的，所有搜索功能都不区分大小写。

### Q: 如何进行更复杂的搜索？

**A:** 可以组合使用多种搜索方法：

```python
def advanced_search(client, query, author=None, year=None):
    """高级搜索示例"""
    # 先进行关键词搜索
    results = client.search_items(query)

    # 然后进行本地筛选
    filtered_results = []
    for item in results:
        data = item['data']

        # 筛选作者
        if author:
            creators = data.get('creators', [])
            author_names = [c.get('lastName', '') for c in creators]
            if not any(author.lower() in name.lower() for name in author_names):
                continue

        # 筛选年份
        if year:
            date = data.get('date', '')
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            if not (year_match and year_match.group() == year):
                continue

        filtered_results.append(item)

    return filtered_results
```

### Q: 搜索性能太慢怎么办？

**A:** 对于大型文献库，建议：

1. 使用 `limit` 参数限制结果数量
2. 避免频繁搜索，考虑缓存结果
3. 使用更具体的搜索条件
4. 考虑使用顶层文献搜索而不是全库搜索

```python
# 推荐的做法
items = client.search_items("specific query")

# 避免的做法
all_items = client.get_items()  # 对于大型库很慢
```

## 错误处理

### Q: 常见的错误类型有哪些？

**A:** 主要有以下几种错误：

```python
from zoteroapi import (
    ZoteroLocalError,    # 基础错误
    ConnectionError,     # 连接错误
    ResourceNotFound,   # 资源不存在
    APIError           # API 调用错误
)

try:
    item = client.get_item("INVALID_KEY")
except ResourceNotFound:
    print("文献不存在")
except ConnectionError:
    print("无法连接到 Zotero")
except ZoteroLocalError as e:
    print(f"API 错误: {e}")
```

### Q: 连接失败怎么办？

**A:** 检查以下几点：

1. **Zotero 是否运行**：确保 Zotero 桌面应用已启动
2. **本地服务器是否启用**：检查 `extensions.zotero.httpServer.enabled` 设置
3. **端口是否正确**：默认使用 23119 端口
4. **防火墙设置**：确保防火墙没有阻止本地连接

### Q: 资源不存在错误如何处理？

**A:** 这是正常的业务逻辑，应该优雅处理：

```python
def safe_get_item(client, item_key):
    """安全获取文献"""
    try:
        return client.get_item(item_key)
    except ResourceNotFound:
        print(f"文献 {item_key} 不存在")
        return None
    except ZoteroLocalError as e:
        print(f"获取文献失败: {e}")
        return None
```

## 性能优化

### Q: 如何提高 API 调用性能？

**A:** 推荐以下优化策略：

```python
# 1. 使用连接复用（自动实现）
client = ZoteroLocal()  # 内部使用 requests.Session

# 2. 分页获取数据
items = client.get_items_top(limit=50)  # 而不是获取所有数据

# 3. 缓存结果
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_get_item(client, item_key):
    return client.get_item(item_key)

# 4. 批量操作
def batch_get_items(client, item_keys):
    return [client.get_item(key) for key in item_keys]
```

### Q: 内存使用过高怎么办？

**A:** 对于大型数据集，注意内存管理：

```python
# 处理大量文献时使用生成器
def process_large_library(client):
    limit = 100
    offset = 0

    while True:
        items = client.get_items_top(limit=limit)
        if not items:
            break

        for item in items:
            yield item  # 使用生成器而不是列表

        offset += limit
```

### Q: 如何监控 API 性能？

**A:** 可以添加性能监控：

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            print(f"{func.__name__} 执行时间: {duration:.3f} 秒")
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"{func.__name__} 执行失败 (耗时: {duration:.3f} 秒): {e}")
            raise
    return wrapper

# 使用
client = ZoteroLocal()
client.get_item = monitor_performance(client.get_item)
```

## 开发和调试

### Q: 如何启用调试模式？

**A:** 使用 Python 的 logging 模块：

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 或者只启用 ZoteroAPI 的日志
logger = logging.getLogger('zoteroapi')
logger.setLevel(logging.DEBUG)
```

### Q: 如何查看 HTTP 请求详情？

**A:** 可以使用 `requests` 的调试功能：

```python
import requests
import urllib3

# 启用 HTTP 调试
urllib3.disable_warnings()
urllib3.add_stderr_logger()
```

### Q: 如何进行单元测试？

**A:** 使用 pytest 和 mocking：

```python
import pytest
from unittest.mock import Mock

def test_get_item():
    # Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {"key": "TEST", "data": {"title": "Test"}}

    # 使用 patch 替换 HTTP 请求
    with pytest.mock.patch('requests.Session.request', return_value=mock_response):
        client = ZoteroLocal()
        item = client.get_item("TEST")
        assert item['data']['title'] == "Test"
```

## 集成和部署

### Q: 如何在生产环境中使用？

**A:** 生产环境建议：

```python
import logging
from zoteroapi import ZoteroLocal

# 配置日志
logging.basicConfig(level=logging.INFO)

# 使用重试机制
import time
from zoteroapi.exceptions import ZoteroLocalError

def robust_api_call(func, max_retries=3, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ZoteroLocalError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避

# 使用
client = ZoteroLocal()
item = robust_api_call(client.get_item, "ITEM_KEY")
```

### Q: 如何集成到 Web 应用中？

**A:** 示例 Flask 集成：

```python
from flask import Flask, jsonify
from zoteroapi import ZoteroLocal

app = Flask(__name__)

# 全局客户端
client = ZoteroLocal()

@app.route('/api/items')
def get_items():
    try:
        items = client.get_items_top(limit=10)
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Q: 如何处理并发访问？

**A:** ZoteroAPI 客户端不是线程安全的，建议：

```python
import threading
from zoteroapi import ZoteroLocal

# 线程本地存储
thread_local = threading.local()

def get_client():
    if not hasattr(thread_local, 'client'):
        thread_local.client = ZoteroLocal()
    return thread_local.client

# 在多线程环境中使用
def worker():
    client = get_client()
    items = client.get_items_top()
```

## 其他问题

### Q: 支持哪些操作系统？

**A:** 支持 Windows、macOS 和 Linux。

### Q: 如何获取帮助？

**A:** 可以通过以下方式获取帮助：

1. 查看 [文档](https://yourusername.github.io/zoteroapi/)
2. 搜索 [Issues](https://github.com/yourusername/zoteroapi/issues)
3. 创建新的 Issue 或加入 [Discussions](https://github.com/yourusername/zoteroapi/discussions)
4. 查看示例代码

### Q: 如何报告 Bug？

**A:** 提交 Bug 报告时请包含：

1. Python 版本
2. Zotero 版本
3. 操作系统
4. 最小可复现代码
5. 完整的错误信息和堆栈跟踪
6. 预期行为和实际行为的描述

### Q: 如何贡献代码？

**A:** 请查看 [贡献指南](development/contributing.md) 了解详细信息。

---

如果您的问题没有在这里找到答案，请在 GitHub 上创建新的 Issue 或 Discussion。我们会尽力帮助您解决问题！