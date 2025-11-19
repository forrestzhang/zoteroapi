# 搜索功能

ZoteroAPI 提供了多种搜索方式，帮助你快速定位文献。

## 通用搜索

使用关键词搜索文献：

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# 搜索包含关键词的文献
results = client.search_items("machine learning")

print(f"找到 {len(results)} 篇相关文献")
for item in results[:5]:  # 显示前 5 个结果
    title = item.get('data', {}).get('title', '无标题')
    print(f"  - {title}")
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| query | str | 搜索关键词 |

**返回值**：匹配的文献条目列表

!!! tip "搜索范围"
    通用搜索会在文献的标题、摘要、标签等字段中查找匹配的内容。

## 按 DOI 搜索

通过 DOI（数字对象标识符）精确查找文献：

```python
# 通过 DOI 搜索
doi = "10.1038/nature12373"
results = client.search_by_doi(doi)

if results:
    item = results[0]
    title = item.get('data', {}).get('title', '无标题')
    print(f"找到文献: {title}")
else:
    print("未找到该 DOI 对应的文献")
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| doi | str | DOI 标识符（不区分大小写） |

**返回值**：匹配的文献列表（通常只有一个或零个）

!!! note "DOI 格式"
    DOI 可以是完整格式（`10.1038/nature12373`）或带前缀（`doi:10.1038/nature12373`），搜索时会自动处理。

## 按 PMID 搜索

通过 PubMed ID 搜索医学文献：

```python
# 通过 PMID 搜索
pmid = "12345678"
results = client.search_by_pmid(pmid)

if results:
    for item in results:
        title = item.get('data', {}).get('title', '无标题')
        print(f"  - {title}")
else:
    print("未找到该 PMID 对应的文献")
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| pmid | str | PubMed ID |

**返回值**：匹配的文献列表

!!! info "PMID 存储位置"
    PMID 通常存储在文献的 `extra` 字段中，格式为 `PMID: 12345678`。

## 按标题搜索

通过标题搜索文献，支持精确匹配和模糊匹配：

### 模糊匹配（默认）

```python
# 模糊匹配（部分标题）
results = client.search_by_title("deep learning", exact_match=False)

print(f"找到 {len(results)} 篇包含 'deep learning' 的文献")
```

### 精确匹配

```python
# 精确匹配（完整标题）
results = client.search_by_title(
    "Attention Is All You Need", 
    exact_match=True
)

if results:
    print("找到精确匹配的文献")
else:
    print("未找到完全匹配的文献")
```

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | str | - | 要搜索的标题 |
| exact_match | bool | False | 是否精确匹配 |

**返回值**：匹配的文献列表

!!! tip "搜索建议"
    - 模糊匹配对大小写不敏感
    - 精确匹配要求标题完全一致（忽略大小写）
    - 如果不确定完整标题，建议使用模糊匹配

## 搜索结果处理

### 提取关键信息

```python
results = client.search_items("neural networks")

for item in results:
    data = item.get('data', {})
    
    # 基本信息
    title = data.get('title', '无标题')
    item_type = data.get('itemType', 'unknown')
    date = data.get('date', '未知')
    
    # 作者信息
    creators = data.get('creators', [])
    authors = ', '.join([
        f"{c.get('lastName', '')} {c.get('firstName', '')}"
        for c in creators[:3]  # 只显示前 3 个作者
    ])
    if len(creators) > 3:
        authors += ' et al.'
    
    # 摘要
    abstract = data.get('abstractNote', '')[:100]  # 前 100 字符
    
    print(f"\n[{item_type}] {title}")
    if authors:
        print(f"作者: {authors}")
    print(f"日期: {date}")
    if abstract:
        print(f"摘要: {abstract}...")
```

### 按相关性排序

```python
# 注意：API 本身不提供相关性排序
# 可以在应用层基于关键词出现次数等指标进行排序

query = "machine learning"
results = client.search_items(query)

# 简单的相关性评分示例
def calculate_relevance(item, query):
    """基于关键词出现次数计算相关性"""
    text = ""
    data = item.get('data', {})
    text += data.get('title', '').lower() + " "
    text += data.get('abstractNote', '').lower() + " "
    tags = data.get('tags', [])
    text += " ".join([t.get('tag', '').lower() for t in tags])
    
    return text.count(query.lower())

# 按相关性排序
sorted_results = sorted(
    results, 
    key=lambda x: calculate_relevance(x, query),
    reverse=True
)

print("按相关性排序的结果：")
for i, item in enumerate(sorted_results[:10], 1):
    title = item.get('data', {}).get('title', '无标题')
    score = calculate_relevance(item, query)
    print(f"{i}. {title} (相关性: {score})")
```

## 组合搜索

结合多种搜索条件：

```python
# 先通过关键词搜索，再过滤期刊文章
results = client.search_items("deep learning")

journal_articles = [
    item for item in results
    if item.get('data', {}).get('itemType') == 'journalArticle'
]

print(f"期刊文章: {len(journal_articles)} 篇")
```

### 多关键词搜索

```python
keywords = ["machine learning", "neural networks", "deep learning"]
all_results = []

for keyword in keywords:
    results = client.search_items(keyword)
    all_results.extend(results)

# 去重（基于 key）
unique_items = {item['key']: item for item in all_results}
print(f"共找到 {len(unique_items)} 篇不重复的文献")
```

### 带标签过滤的搜索

```python
results = client.search_items("AI")

# 只保留带有特定标签的文献
target_tag = "重要"
filtered_results = []

for item in results:
    tags = item.get('data', {}).get('tags', [])
    tag_names = [t.get('tag', '') for t in tags]
    
    if target_tag in tag_names:
        filtered_results.append(item)

print(f"找到 {len(filtered_results)} 篇带标签 '{target_tag}' 的文献")
```

## 搜索性能优化

### 缓存搜索结果

```python
class ZoteroSearchCache:
    def __init__(self, client):
        self.client = client
        self.cache = {}
    
    def search(self, query):
        """带缓存的搜索"""
        if query in self.cache:
            print(f"从缓存返回结果: {query}")
            return self.cache[query]
        
        results = self.client.search_items(query)
        self.cache[query] = results
        return results

# 使用缓存
client = ZoteroLocal()
search_cache = ZoteroSearchCache(client)

# 第一次搜索，访问 API
results1 = search_cache.search("machine learning")

# 第二次搜索，从缓存返回
results2 = search_cache.search("machine learning")
```

### 限制搜索范围

如果文献库很大，可以先获取特定集合或最近的文献，再进行搜索：

```python
# 只在最近的 100 篇文献中搜索
recent_items = client.get_items_top(limit=100)

query = "deep learning"
filtered = [
    item for item in recent_items
    if query.lower() in item.get('data', {}).get('title', '').lower()
]

print(f"在最近的文献中找到 {len(filtered)} 篇")
```

## 实用搜索示例

### 查找某个作者的所有文献

```python
def search_by_author(client, author_name):
    """搜索某个作者的文献"""
    all_items = client.get_items_top(limit=200)
    author_items = []
    
    for item in all_items:
        creators = item.get('data', {}).get('creators', [])
        for creator in creators:
            full_name = f"{creator.get('firstName', '')} {creator.get('lastName', '')}".lower()
            if author_name.lower() in full_name:
                author_items.append(item)
                break
    
    return author_items

# 使用
results = search_by_author(client, "张三")
print(f"找到张三的 {len(results)} 篇文献")
```

### 查找某年发表的文献

```python
def search_by_year(client, year):
    """搜索某一年发表的文献"""
    all_items = client.get_items_top(limit=200)
    year_items = []
    
    for item in all_items:
        date = item.get('data', {}).get('date', '')
        if str(year) in date:
            year_items.append(item)
    
    return year_items

# 查找 2024 年的文献
results = search_by_year(client, 2024)
print(f"2024 年发表: {len(results)} 篇")
```

### 查找未读文献

```python
# 查找带有 "未读" 标签的文献
def find_unread(client):
    items = client.get_items_top(limit=100)
    unread = []
    
    for item in items:
        tags = item.get('data', {}).get('tags', [])
        tag_names = [t.get('tag', '') for t in tags]
        
        if "未读" in tag_names or "_READ_" in tag_names:
            unread.append(item)
    
    return unread

unread_items = find_unread(client)
print(f"未读文献: {len(unread_items)} 篇")
```

## 错误处理

```python
from zoteroapi import ZoteroLocalError

try:
    results = client.search_items("AI")
    print(f"找到 {len(results)} 篇文献")
except ZoteroLocalError as e:
    print(f"搜索失败: {e}")
```

## 最佳实践

1. **选择合适的搜索方法**：
   - 已知 DOI：使用 `search_by_doi()`
   - 医学文献：使用 `search_by_pmid()`
   - 记得部分标题：使用 `search_by_title(exact_match=False)`
   - 关键词搜索：使用 `search_items()`

2. **处理空结果**：

```python
results = client.search_items("rare keyword")
if not results:
    print("未找到相关文献，请尝试其他关键词")
else:
    # 处理结果
    pass
```

3. **搜索效率**：
   - 对于大型文献库，考虑使用缓存
   - 尽可能缩小搜索范围
   - 使用更精确的搜索方法（如 DOI）

## 下一步

- 📚 [文献条目管理](items-management.md)
- 📝 [笔记管理](notes.md)
- 📎 [文件操作](files.md)
- 💡 [搜索示例](../examples/search-examples.md)

## 相关资源

- [API 参考 - SearchMixin](../api-reference/mixins/search.md)
- [示例代码 - 搜索示例](../examples/search-examples.md)
