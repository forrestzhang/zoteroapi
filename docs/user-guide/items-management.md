# 文献条目管理

本页面介绍如何使用 ZoteroAPI 管理 Zotero 文献库中的条目。

## 获取文献条目

### 获取顶层条目

顶层条目是指文献库中的主条目，不包括笔记和附件等子条目：

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# 获取最近的 10 篇顶层条目
items = client.get_items_top(limit=10)

for item in items:
    title = item.get('data', {}).get('title', '无标题')
    item_type = item.get('data', {}).get('itemType', 'unknown')
    print(f"[{item_type}] {title}")
```

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 10 | 限制返回的条目数量 |

**返回值**：包含文献条目信息的字典列表

### 获取所有条目

获取文献库中的所有条目（包括子条目）：

```python
# 获取所有条目（不限制数量）
all_items = client.get_items()

# 限制返回数量
limited_items = client.get_items(limit=50)

print(f"总共 {len(all_items)} 个条目")
```

!!! warning "性能提示"
    对于大型文献库，获取所有条目可能需要较长时间。建议使用 `limit` 参数控制返回数量。

### 获取单个条目

通过 key 获取特定条目的详细信息：

```python
# 假设已知条目的 key
item_key = "ABC123XYZ"

# 获取条目详情
item = client.get_item(item_key)

# 提取信息
data = item.get('data', {})
print(f"标题: {data.get('title')}")
print(f"类型: {data.get('itemType')}")
print(f"日期: {data.get('date')}")
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| item_key | str | 条目的唯一标识符 |

**返回值**：包含完整条目信息的字典

## 条目数据结构

每个文献条目都包含以下主要字段：

```python
{
    "key": "ABC123XYZ",           # 条目唯一标识
    "version": 123,                # 版本号
    "library": {...},              # 所属库信息
    "links": {                     # 相关链接
        "self": {...},
        "alternate": {...}
    },
    "meta": {                      # 元数据
        "creatorSummary": "张三, 李四",
        "parsedDate": "2024-01-15",
        "numChildren": 2
    },
    "data": {                      # 核心数据
        "key": "ABC123XYZ",
        "version": 123,
        "itemType": "journalArticle",
        "title": "深度学习研究",
        "creators": [              # 作者信息
            {
                "creatorType": "author",
                "firstName": "三",
                "lastName": "张"
            }
        ],
        "abstractNote": "摘要内容...",
        "publicationTitle": "期刊名称",
        "volume": "10",
        "issue": "2",
        "pages": "123-145",
        "date": "2024-01-15",
        "DOI": "10.1234/example.doi",
        "url": "https://example.com",
        "tags": [                  # 标签
            {"tag": "机器学习"},
            {"tag": "深度学习"}
        ],
        "collections": [],         # 所属文献集
        "relations": {}
    }
}
```

### 核心字段说明

| 字段路径 | 说明 | 示例 |
|----------|------|------|
| `key` | 条目唯一标识 | "ABC123XYZ" |
| `data.itemType` | 条目类型 | "journalArticle", "book", "conferencePaper" |
| `data.title` | 标题 | "深度学习研究" |
| `data.creators` | 作者列表 | 见上方数据结构 |
| `data.date` | 发布日期 | "2024-01-15" |
| `data.DOI` | DOI 标识符 | "10.1234/example.doi" |
| `data.tags` | 标签列表 | [{"tag": "机器学习"}] |
| `meta.numChildren` | 子项数量（笔记、附件等） | 2 |

### 常见条目类型

| itemType | 说明 | 常见字段 |
|----------|------|----------|
| journalArticle | 期刊文章 | publicationTitle, volume, issue, pages |
| book | 图书 | publisher, place, ISBN |
| conferencePaper | 会议论文 | conferenceName, proceedingsTitle |
| thesis | 学位论文 | university, thesisType |
| webpage | 网页 | websiteTitle, accessDate |
| note | 笔记 | note (HTML 内容) |
| attachment | 附件 | contentType, filename |

## 获取文献集

### 获取所有文献集

```python
# 获取所有文献集
collections = client.get_collections()

for collection in collections:
    data = collection.get('data', {})
    name = data.get('name', '未命名')
    parent = data.get('parentCollection', False)
    
    # 判断是否为子文献集
    level = "  " if parent else ""
    print(f"{level}📁 {name}")
```

**返回值**：文献集对象列表，每个对象包含：

- `key`：文献集唯一标识
- `data.name`：文献集名称
- `data.parentCollection`：父文献集 key（如有）

### 获取单个文献集

```python
# 获取特定文献集的信息
collection_key = "COLL123"
collection = client.get_collection(collection_key)

data = collection.get('data', {})
print(f"文献集名称: {data.get('name')}")
print(f"包含条目数: {data.get('numItems', 0)}")
```

### 获取文献集中的条目

```python
# 获取文献集中的所有条目
collection_key = "COLL123"
items = client.get_collection_items(collection_key)

print(f"该文献集包含 {len(items)} 篇文献")

for item in items:
    title = item.get('data', {}).get('title', '无标题')
    print(f"  - {title}")
```

## 获取标签

```python
# 获取所有标签
tags = client.get_tags()

print(f"共有 {len(tags)} 个标签：")
for tag in tags:
    tag_name = tag.get('tag', '')
    num_items = tag.get('meta', {}).get('numItems', 0)
    print(f"  - {tag_name} ({num_items} 篇)")
```

## 实用示例

### 按类型分类统计

```python
from collections import Counter

items = client.get_items_top(limit=100)

# 统计各类型文献数量
item_types = [item.get('data', {}).get('itemType', 'unknown') for item in items]
type_counts = Counter(item_types)

print("文献类型分布：")
for item_type, count in type_counts.most_common():
    print(f"  {item_type}: {count}")
```

### 查找最近添加的文献

```python
# 获取最近的文献
recent_items = client.get_items_top(limit=10)

print("最近添加的文献：")
for i, item in enumerate(recent_items, 1):
    data = item.get('data', {})
    title = data.get('title', '无标题')
    date = data.get('date', '未知日期')
    print(f"{i}. {title} ({date})")
```

### 查找带有特定标签的文献

```python
# 获取所有文献
items = client.get_items_top(limit=100)

# 筛选带有特定标签的文献
target_tag = "机器学习"
tagged_items = []

for item in items:
    tags = item.get('data', {}).get('tags', [])
    tag_names = [t.get('tag', '') for t in tags]
    
    if target_tag in tag_names:
        tagged_items.append(item)

print(f"带有标签 '{target_tag}' 的文献：{len(tagged_items)} 篇")
```

### 导出文献信息为 CSV

```python
import csv

# 获取文献
items = client.get_items_top(limit=50)

# 导出为 CSV
with open('zotero_items.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['标题', '类型', '作者', '日期', 'DOI'])
    
    for item in items:
        data = item.get('data', {})
        title = data.get('title', '')
        item_type = data.get('itemType', '')
        
        # 提取作者
        creators = data.get('creators', [])
        authors = ', '.join([
            f"{c.get('lastName', '')} {c.get('firstName', '')}" 
            for c in creators
        ])
        
        date = data.get('date', '')
        doi = data.get('DOI', '')
        
        writer.writerow([title, item_type, authors, date, doi])

print("已导出到 zotero_items.csv")
```

## 分页与性能

### 使用 limit 参数

```python
# 分批获取文献，避免一次性加载过多
BATCH_SIZE = 50

def process_items_in_batches():
    offset = 0
    while True:
        # 注意：当前 API 可能不直接支持 offset
        # 这里展示概念性用法
        items = client.get_items_top(limit=BATCH_SIZE)
        
        if not items:
            break
        
        # 处理当前批次
        for item in items:
            title = item.get('data', {}).get('title', '')
            print(f"处理: {title}")
        
        # 如果返回数量少于 BATCH_SIZE，说明已到末尾
        if len(items) < BATCH_SIZE:
            break
```

### 性能优化建议

1. **使用 limit 参数**：始终指定合理的 limit 值
2. **缓存结果**：对于不常变化的数据（如文献集列表），可以在应用层缓存
3. **批量处理**：避免在循环中频繁调用 API
4. **按需获取**：只获取需要的数据，而不是全部

## 错误处理

```python
from zoteroapi import ZoteroLocalError, ResourceNotFound

client = ZoteroLocal()

try:
    # 尝试获取可能不存在的条目
    item = client.get_item("INVALID_KEY")
except ResourceNotFound:
    print("条目不存在")
except ZoteroLocalError as e:
    print(f"API 错误: {e}")
```

## 最佳实践

### 1. 安全访问嵌套数据

```python
# ✅ 使用 get() 方法提供默认值
title = item.get('data', {}).get('title', '无标题')

# ❌ 直接访问可能导致 KeyError
# title = item['data']['title']
```

### 2. 检查条目类型

```python
item = client.get_item(item_key)
item_type = item.get('data', {}).get('itemType')

if item_type == 'journalArticle':
    journal = item.get('data', {}).get('publicationTitle')
    print(f"期刊: {journal}")
elif item_type == 'book':
    publisher = item.get('data', {}).get('publisher')
    print(f"出版社: {publisher}")
```

### 3. 过滤和筛选

```python
# 只获取期刊文章
items = client.get_items_top(limit=100)
journal_articles = [
    item for item in items
    if item.get('data', {}).get('itemType') == 'journalArticle'
]
```

## 下一步

- 🔍 [学习搜索功能](search.md)
- 📁 [管理文献集](collections.md)
- 📝 [添加和管理笔记](notes.md)
- 🏷️ [使用标签功能](tags.md)

## 相关资源

- [API 参考 - ZoteroLocal](../api-reference/client.md)
- [快速上手示例](../getting-started/quick-start.md)
- [示例代码 - 基础用法](../examples/basic-usage.md)
