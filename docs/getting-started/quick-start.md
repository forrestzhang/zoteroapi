# 快速上手

本教程将在 5 分钟内带你完成 ZoteroAPI 的第一次使用，体验核心功能。

## 前置准备

在开始之前，请确保：

- [x] 已安装 ZoteroAPI（参见 [安装指南](installation.md)）
- [x] Zotero 桌面应用正在运行
- [x] 已启用 Zotero 本地服务器（参见 [配置指南](configuration.md)）

## 第一步：初始化客户端

创建一个 Python 文件（如 `quick_start.py`），导入并初始化客户端：

```python
from zoteroapi import ZoteroLocal

# 初始化客户端（使用默认配置）
client = ZoteroLocal()
```

!!! tip "自定义配置"
    如果你修改了 Zotero 的默认端口，可以这样初始化：
    ```python
    client = ZoteroLocal(base_url="http://localhost:23120")
    ```

## 第二步：获取文献条目

让我们获取你的前 10 篇文献：

```python
# 获取顶层文献条目
items = client.get_items_top(limit=10)

# 打印文献标题
print(f"找到 {len(items)} 篇文献：\n")
for i, item in enumerate(items, 1):
    title = item.get('data', {}).get('title', '无标题')
    item_type = item.get('data', {}).get('itemType', 'unknown')
    print(f"{i}. [{item_type}] {title}")
```

**预期输出：**
```
找到 10 篇文献：

1. [journalArticle] Deep Learning in Neural Networks
2. [book] Python Programming: An Introduction
3. [conferencePaper] Attention Is All You Need
...
```

## 第三步：搜索文献

尝试搜索包含特定关键词的文献：

```python
# 搜索关键词
query = "machine learning"
results = client.search_items(query)

print(f"\n搜索 '{query}' 找到 {len(results)} 篇相关文献：\n")

# 显示前 5 个结果
for i, item in enumerate(results[:5], 1):
    data = item.get('data', {})
    title = data.get('title', '无标题')
    # 获取作者信息
    creators = data.get('creators', [])
    authors = ', '.join([c.get('lastName', '') for c in creators[:2]])
    if len(creators) > 2:
        authors += ' et al.'
    
    print(f"{i}. {title}")
    if authors:
        print(f"   作者: {authors}")
```

## 第四步：获取文献详情

选择一篇文献，查看其详细信息：

```python
# 获取第一篇文献的 key
if items:
    item_key = items[0]['key']
    
    # 获取详细信息
    item_detail = client.get_item(item_key)
    
    # 提取关键信息
    data = item_detail.get('data', {})
    print(f"\n文献详情：")
    print(f"标题: {data.get('title', '无标题')}")
    print(f"类型: {data.get('itemType', 'unknown')}")
    print(f"日期: {data.get('date', '未知')}")
    
    # 获取标签
    tags = data.get('tags', [])
    if tags:
        tag_names = [tag.get('tag', '') for tag in tags]
        print(f"标签: {', '.join(tag_names)}")
```

## 第五步：添加笔记

为文献添加一条笔记：

```python
# 为第一篇文献添加笔记
if items:
    item_key = items[0]['key']
    note_text = "这是通过 ZoteroAPI 添加的测试笔记！"
    
    try:
        note = client.add_item_note(
            item_key=item_key,
            note_text=note_text,
            title="快速上手测试笔记"
        )
        print(f"\n✅ 成功添加笔记！")
        print(f"笔记 Key: {note.get('key', 'N/A')}")
    except Exception as e:
        print(f"❌ 添加笔记失败: {e}")
```

## 第六步：获取文献集

查看你的所有文献集：

```python
# 获取所有文献集
collections = client.get_collections()

print(f"\n文献集列表（共 {len(collections)} 个）：\n")
for i, coll in enumerate(collections[:5], 1):
    data = coll.get('data', {})
    name = data.get('name', '未命名')
    parent = data.get('parentCollection', False)
    level = "  " if parent else ""
    print(f"{level}{i}. {name}")
```

## 完整示例代码

将以上步骤整合到一起：

```python
from zoteroapi import ZoteroLocal, ZoteroLocalError

def main():
    """ZoteroAPI 快速上手示例"""
    
    # 初始化客户端
    client = ZoteroLocal()
    
    try:
        # 1. 获取文献条目
        print("=" * 50)
        print("步骤 1: 获取文献条目")
        print("=" * 50)
        items = client.get_items_top(limit=10)
        print(f"找到 {len(items)} 篇文献\n")
        
        # 2. 搜索文献
        print("=" * 50)
        print("步骤 2: 搜索文献")
        print("=" * 50)
        results = client.search_items("machine learning")
        print(f"搜索结果: {len(results)} 篇\n")
        
        # 3. 查看文献详情
        if items:
            print("=" * 50)
            print("步骤 3: 查看文献详情")
            print("=" * 50)
            item_key = items[0]['key']
            item = client.get_item(item_key)
            title = item.get('data', {}).get('title', '无标题')
            print(f"标题: {title}\n")
            
            # 4. 添加笔记
            print("=" * 50)
            print("步骤 4: 添加笔记")
            print("=" * 50)
            note = client.add_item_note(
                item_key=item_key,
                note_text="快速上手测试笔记"
            )
            print(f"✅ 笔记已添加\n")
        
        # 5. 获取文献集
        print("=" * 50)
        print("步骤 5: 获取文献集")
        print("=" * 50)
        collections = client.get_collections()
        print(f"文献集数量: {len(collections)}\n")
        
        print("=" * 50)
        print("🎉 快速上手完成！")
        print("=" * 50)
        
    except ZoteroLocalError as e:
        print(f"❌ API 错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == "__main__":
    main()
```

## 运行示例

保存代码为 `quick_start.py`，然后在终端运行：

```bash
python quick_start.py
```

## 常见错误处理

### 连接失败

```python
from zoteroapi import ZoteroLocal, ZoteroLocalError

try:
    client = ZoteroLocal()
    items = client.get_items_top(limit=5)
except ZoteroLocalError as e:
    print(f"API 错误: {e}")
    print("请检查：")
    print("1. Zotero 是否正在运行")
    print("2. 本地服务器是否已启用")
    print("3. 端口配置是否正确")
```

### 空数据处理

```python
items = client.get_items_top(limit=10)

if not items:
    print("当前库中没有文献条目")
else:
    for item in items:
        # 安全获取数据，提供默认值
        data = item.get('data', {})
        title = data.get('title', '无标题')
        item_type = data.get('itemType', 'unknown')
        print(f"[{item_type}] {title}")
```

## 下一步学习

恭喜完成快速上手！接下来你可以：

- 📚 **深入学习各项功能**：
  - [文献条目管理](../user-guide/items-management.md)
  - [搜索功能](../user-guide/search.md)
  - [笔记管理](../user-guide/notes.md)
  - [文件操作](../user-guide/files.md)

- 💡 **查看更多示例**：
  - [基础用法示例](../examples/basic-usage.md)
  - [搜索示例](../examples/search-examples.md)
  - [高级工作流](../examples/advanced-workflows.md)

- 🔍 **探索完整 API**：
  - [API 参考文档](../api-reference/index.md)
  - [ZoteroLocal 客户端](../api-reference/client.md)

## 实用技巧

### 使用上下文管理器（未来功能）

```python
# 注意：当前版本不支持，这是规划中的功能
# with ZoteroLocal() as client:
#     items = client.get_items_top(limit=10)
```

### 批量操作

```python
# 批量获取多个文献集的条目
collections = client.get_collections()

for collection in collections[:3]:  # 处理前 3 个文献集
    coll_key = collection['key']
    coll_name = collection['data']['name']
    items = client.get_collection_items(coll_key)
    print(f"{coll_name}: {len(items)} 篇文献")
```

### 数据过滤

```python
# 获取所有期刊文章
items = client.get_items_top(limit=100)
journal_articles = [
    item for item in items 
    if item.get('data', {}).get('itemType') == 'journalArticle'
]
print(f"期刊文章数量: {len(journal_articles)}")
```

## 需要帮助？

- 📖 查看 [常见问题](../faq.md)
- 🐛 [报告问题](https://github.com/yourusername/zoteroapi/issues)
- 💬 [社区讨论](https://github.com/yourusername/zoteroapi/discussions)
