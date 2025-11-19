# 基础用法示例

本文档提供了 ZoteroAPI 的基础用法示例，帮助新手快速上手。

## 安装和导入

```bash
pip install zoteroapi
```

```python
from zoteroapi import ZoteroLocal
from zoteroapi import ZoteroLocalError, ResourceNotFound
```

## 创建客户端

```python
# 使用默认配置（localhost:23119）
client = ZoteroLocal()

# 使用自定义配置
custom_client = ZoteroLocal(
    base_url="http://localhost:23120/api/users/000000/"
)
```

## 获取文献

### 获取最近的文献

```python
# 获取前 10 个顶层文献
items = client.get_items_top(limit=10)

print("最近添加的文献：")
for item in items:
    title = item.get('data', {}).get('title', '无标题')
    creators = item.get('data', {}).get('creators', [])

    # 提取作者信息
    if creators:
        author = creators[0].get('lastName', '') + ', ' + creators[0].get('firstName', '')
    else:
        author = '未知作者'

    print(f"- {title} ({author})")
```

### 获取单个文献

```python
try:
    item = client.get_item("ABC123XYZ")  # 替换为实际的 item_key

    title = item['data']['title']
    abstract = item['data'].get('abstractNote', '无摘要')

    print(f"标题: {title}")
    print(f"摘要: {abstract[:200]}..." if len(abstract) > 200 else f"摘要: {abstract}")

except ResourceNotFound:
    print("文献不存在")
except ZoteroLocalError as e:
    print(f"获取文献失败: {e}")
```

## 获取文献集

```python
# 获取所有文献集
collections = client.get_collections()

print("文献集列表：")
for collection in collections:
    name = collection['data']['name']
    num_items = collection['data'].get('numItems', 0)
    print(f"- {name} ({num_items} 篇文献)")

# 获取特定文献集中的文献
if collections:
    first_collection_key = collections[0]['key']
    collection_items = client.get_collection_items(first_collection_key)

    print(f"\n'{collections[0]['data']['name']}' 中的文献：")
    for item in collection_items[:5]:  # 只显示前 5 篇
        print(f"- {item['data']['title']}")
```

## 基础搜索

### 关键词搜索

```python
# 搜索包含 "机器学习" 的文献
results = client.search_items("机器学习")

print(f"找到 {len(results)} 篇相关文献：")
for item in results[:5]:  # 只显示前 5 个结果
    title = item['data']['title']
    print(f"- {title}")
```

### DOI 搜索

```python
# 通过 DOI 搜索
doi_results = client.search_by_doi("10.1038/nature12373")

if doi_results:
    print("找到对应 DOI 的文献：")
    item = doi_results[0]
    print(f"- {item['data']['title']}")
else:
    print("未找到该 DOI 对应的文献")
```

### PMID 搜索

```python
# 通过 PubMed ID 搜索
pmid_results = client.search_by_pmid("12345678")

if pmid_results:
    print("找到对应 PMID 的文献：")
    for item in pmid_results:
        print(f"- {item['data']['title']}")
else:
    print("未找到该 PMID 对应的文献")
```

### 标题搜索

```python
# 模糊搜索标题
title_results = client.search_by_title("深度学习")
print(f"标题包含 '深度学习' 的文献: {len(title_results)} 篇")

# 精确搜索标题
exact_results = client.search_by_title("深度学习", exact_match=True)
print(f"标题完全匹配 '深度学习' 的文献: {len(exact_results)} 篇")
```

## 获取标签

```python
# 获取所有标签
tags = client.get_tags()

print(f"共有 {len(tags)} 个标签:")
for tag in tags[:15]:  # 显示前 15 个标签
    print(f"- {tag}")
```

## 错误处理

```python
def safe_get_item(client, item_key):
    """安全地获取文献，包含完整的错误处理"""
    try:
        item = client.get_item(item_key)

        # 验证返回的数据
        if not item or 'data' not in item:
            print("返回的数据格式不正确")
            return None

        title = item['data'].get('title', '无标题')
        print(f"成功获取文献: {title}")
        return item

    except ResourceNotFound:
        print(f"文献 {item_key} 不存在")
    except ConnectionError:
        print("无法连接到 Zotero，请确保 Zotero 正在运行")
    except ZoteroLocalError as e:
        print(f"API 错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

    return None

# 使用示例
item = safe_get_item(client, "INVALID_KEY")
```

## 实用工具函数

### 文献信息提取

```python
def extract_citation_info(item):
    """提取文献的引用信息"""
    data = item.get('data', {})

    # 基本信息
    title = data.get('title', '无标题')
    item_type = data.get('itemType', 'unknown')

    # 作者信息
    creators = data.get('creators', [])
    authors = []
    for creator in creators:
        if creator.get('creatorType') == 'author':
            last_name = creator.get('lastName', '')
            first_name = creator.get('firstName', '')
            if last_name and first_name:
                authors.append(f"{last_name}, {first_name[0]}.")
            elif last_name:
                authors.append(last_name)

    # 发表信息
    publication_title = data.get('publicationTitle', '')
    year = data.get('date', '')
    volume = data.get('volume', '')
    pages = data.get('pages', '')

    # 构建引用
    if authors:
        author_text = ', '.join(authors[:3])  # 最多显示 3 个作者
        if len(authors) > 3:
            author_text += ' et al.'
    else:
        author_text = '未知作者'

    citation = f"{author_text} ({year}). {title}."
    if publication_title:
        citation += f" {publication_title}"
    if volume:
        citation += f", {volume}"
    if pages:
        citation += f", {pages}"

    return {
        'title': title,
        'authors': authors,
        'year': year,
        'journal': publication_title,
        'citation': citation
    }

# 使用示例
if items:
    first_item = items[0]
    info = extract_citation_info(first_item)
    print("文献引用信息：")
    print(info['citation'])
```

### 文献统计

```python
def analyze_library(client):
    """分析文献库的基本统计信息"""
    try:
        # 获取所有文献
        all_items = client.get_items()
        collections = client.get_collections()
        tags = client.get_tags()

        # 统计不同类型的文献
        item_types = {}
        for item in all_items:
            item_type = item.get('data', {}).get('itemType', 'unknown')
            item_types[item_type] = item_types.get(item_type, 0) + 1

        print("=" * 40)
        print("文献库统计信息")
        print("=" * 40)
        print(f"总文献数: {len(all_items)}")
        print(f"文献集数: {len(collections)}")
        print(f"标签数: {len(tags)}")
        print()

        print("文献类型分布：")
        for item_type, count in sorted(item_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {item_type}: {count}")

        return {
            'total_items': len(all_items),
            'total_collections': len(collections),
            'total_tags': len(tags),
            'item_types': item_types
        }

    except ZoteroLocalError as e:
        print(f"分析失败: {e}")
        return None

# 运行分析
stats = analyze_library(client)
```

## 完整的示例脚本

```python
#!/usr/bin/env python3
"""
ZoteroAPI 基础使用示例
"""

from zoteroapi import ZoteroLocal, ZoteroLocalError

def main():
    # 创建客户端
    client = ZoteroLocal()

    try:
        print("🔍 正在连接 Zotero...")

        # 测试连接
        collections = client.get_collections()
        print(f"✅ 连接成功！找到 {len(collections)} 个文献集")

        # 获取最近文献
        print("\n📚 最近的文献：")
        recent_items = client.get_items_top(limit=5)
        for i, item in enumerate(recent_items, 1):
            title = item.get('data', {}).get('title', '无标题')
            print(f"{i}. {title}")

        # 搜索示例
        query = "机器学习"
        print(f"\n🔎 搜索 '{query}':")
        search_results = client.search_items(query)
        print(f"找到 {len(search_results)} 篇相关文献")

        # 标签统计
        tags = client.get_tags()
        print(f"\n🏷️  共有 {len(tags)} 个标签")

        # 显示常用标签
        tag_counts = {}
        items = client.get_items()
        for item in items:
            for tag_info in item.get('data', {}).get('tags', []):
                tag = tag_info.get('tag', '')
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print("最常用的标签：")
        for tag, count in top_tags:
            print(f"  {tag}: {count} 次")

    except ZoteroLocalError as e:
        print(f"❌ 操作失败: {e}")
        print("请确保 Zotero 正在运行且已启用本地服务器")

if __name__ == "__main__":
    main()
```

## 运行示例

```bash
# 保存上面的脚本为 zotero_demo.py
python zotero_demo.py
```

预期输出：
```
🔍 正在连接 Zotero...
✅ 连接成功！找到 3 个文献集

📚 最近的文献：
1. 深度学习基础
2. 机器学习算法研究
3. 计算机视觉进展

🔎 搜索 '机器学习':
找到 2 篇相关文献

🏷️  共有 15 个标签
最常用的标签：
  深度学习: 8 次
  机器学习: 6 次
  2024: 5 次
  必读: 4 次
  综述: 3 次
```

## 下一步

- 查看 [搜索示例](search-examples.md) 了解更高级的搜索技巧
- 学习 [文件操作](file-operations.md) 管理附件文件
- 探索 [笔记操作](note-operations.md) 处理文献笔记
- 参考 [高级工作流](advanced-workflows.md) 了解实际应用场景