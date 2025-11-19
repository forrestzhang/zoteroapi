# ZoteroAPI

<div align="center">

**一个简单高效的 Python 客户端库，用于访问本地 Zotero 服务器 API**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 什么是 ZoteroAPI？

ZoteroAPI 是一个轻量级的 Python 客户端库，专为本地 Zotero 服务器设计。它提供了一套简洁的 API，让你能够轻松地：

- 📚 **管理文献条目**：获取、检索和操作你的 Zotero 文献库
- 🔍 **强大的搜索**：通过 DOI、PMID、标题或关键词搜索文献
- 📝 **笔记管理**：创建、获取和管理文献笔记
- 📎 **文件操作**：上传、下载和管理文献附件
- 🏷️ **标签系统**：获取和筛选文献标签

## 核心特性

<div class="grid cards" markdown>

- :material-flash:{ .lg .middle } **简单易用**

    ---

    简洁的 API 设计，5 分钟即可上手

    ```python
    from zoteroapi import ZoteroLocal
    client = ZoteroLocal()
    items = client.get_items_top(limit=10)
    ```

- :material-cog:{ .lg .middle } **功能丰富**

    ---

    支持文献管理、搜索、笔记、文件操作等全方位功能

    [:octicons-arrow-right-24: 查看用户指南](user-guide/items-management.md)

- :material-puzzle:{ .lg .middle } **模块化设计**

    ---

    采用 Mixin 模式，功能模块清晰分离，易于扩展

    [:octicons-arrow-right-24: 了解架构](development/architecture.md)

- :material-file-document:{ .lg .middle } **完整文档**

    ---

    详细的 API 参考、使用示例和开发指南

    [:octicons-arrow-right-24: API 参考](api-reference/index.md)

</div>

## 快速开始

### 安装

使用 pip 安装 ZoteroAPI：

```bash
pip install zoteroapi
```

!!! note "Python 版本要求"
    ZoteroAPI 需要 Python 3.11 或更高版本。

### 5 分钟快速示例

```python
from zoteroapi import ZoteroLocal

# 初始化客户端
client = ZoteroLocal()

# 获取最近的文献条目
items = client.get_items_top(limit=10)
for item in items:
    title = item.get('data', {}).get('title', 'Untitled')
    print(f"📄 {title}")

# 搜索文献
results = client.search_items("machine learning")
print(f"找到 {len(results)} 篇相关文献")

# 添加笔记
item_key = items[0]['key']
note = client.add_item_note(
    item_key=item_key,
    note_text="这是一篇很有价值的论文！"
)
print(f"✅ 笔记已添加")
```

!!! tip "前置要求"
    使用前需要启动 Zotero 并在设置中启用本地服务器。详见 [Zotero 配置指南](getting-started/configuration.md)。

## 主要功能

### 文献管理

快速获取和管理你的 Zotero 文献库：

```python
# 获取所有文献集
collections = client.get_collections()

# 获取特定文献集的条目
items = client.get_collection_items(collection_key)

# 获取文献的详细信息
item = client.get_item(item_key)
```

[:octicons-arrow-right-24: 文献管理详细指南](user-guide/items-management.md)

### 搜索功能

支持多种搜索方式，精准定位文献：

```python
# 通过 DOI 搜索
item = client.search_by_doi("10.1038/nature12373")

# 通过标题搜索
results = client.search_by_title("Deep Learning", exact_match=False)

# 通用关键词搜索
results = client.search_items("neural networks")
```

[:octicons-arrow-right-24: 搜索功能详细指南](user-guide/search.md)

### 文件操作

轻松处理文献附件：

```python
# 下载附件
client.download_file(item_key, save_path)

# 上传文件
client.upload_file(file_path, parent_item=item_key)

# 复制附件到指定目录
client.copy_attachment_to_downloads(file_uri, download_dir)
```

[:octicons-arrow-right-24: 文件操作详细指南](user-guide/files.md)

## 下一步

<div class="grid cards" markdown>

- :material-download:{ .lg .middle } **[安装指南](getting-started/installation.md)**

    了解如何安装和配置 ZoteroAPI

- :material-rocket-launch:{ .lg .middle } **[快速上手](getting-started/quick-start.md)**

    5 分钟学会基本用法

- :material-book-open:{ .lg .middle } **[用户指南](user-guide/client-initialization.md)**

    深入了解各项功能

- :material-code-braces:{ .lg .middle } **[示例代码](examples/basic-usage.md)**

    查看实际使用案例

</div>

## 社区与支持

- 📖 **[文档](https://yourusername.github.io/zoteroapi/)**：完整的使用文档和 API 参考
- 🐛 **[问题反馈](https://github.com/yourusername/zoteroapi/issues)**：报告 bug 或提出功能建议
- 💬 **[讨论区](https://github.com/yourusername/zoteroapi/discussions)**：与社区交流使用经验
- 🤝 **[贡献指南](development/contributing.md)**：参与项目开发

## 许可证

ZoteroAPI 采用 [MIT 许可证](https://opensource.org/licenses/MIT)开源。
