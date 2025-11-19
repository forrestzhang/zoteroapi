# SearchMixin

`SearchMixin` 提供了各种搜索功能的 Mixin 类，包括通用关键词搜索、DOI 搜索、PMID 搜索和标题搜索。

## 类定义

```python
class SearchMixin:
    """搜索功能 Mixin 类"""
```

## 主要方法

### search_items()

```python
def search_items(self, query: str) -> List[Dict]:
    """
    通过关键词搜索文献条目

    在文献库中搜索包含指定关键词的文献。搜索范围包括标题、
    摘要、标签等字段。

    Args:
        query: 搜索关键词字符串

    Returns:
        List[Dict]: 匹配的文献条目列表，每个元素为包含完整条目信息的字典

    Raises:
        ZoteroLocalError: 当 API 请求失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> results = client.search_items("machine learning")
        >>> print(f"找到 {len(results)} 篇相关文献")
        >>> for item in results[:5]:
        ...     title = item['data']['title']
        ...     print(f"  - {title}")

    Note:
        搜索不区分大小写
        搜索范围包括：标题、摘要、标签等字段
    """
```

### search_by_doi()

```python
def search_by_doi(self, doi: str) -> List[Dict]:
    """
    通过 DOI 搜索文献

    使用 DOI（数字对象标识符）精确查找文献。DOI 匹配不区分大小写。

    Args:
        doi: DOI 标识符，如 '10.1038/nature12373'

    Returns:
        List[Dict]: 匹配的文献列表（通常只有 0 个或 1 个结果）

    Raises:
        ZoteroLocalError: 当搜索失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> results = client.search_by_doi("10.1038/nature12373")
        >>> if results:
        ...     print(f"找到文献: {results[0]['data']['title']}")
        ... else:
        ...     print("未找到该 DOI 对应的文献")

    Note:
        DOI 匹配不区分大小写
        返回结果通常为空列表或包含一个元素的列表
    """
```

### search_by_pmid()

```python
def search_by_pmid(self, pmid: str) -> List[Dict]:
    """
    通过 PubMed ID 搜索文献

    使用 PubMed ID 搜索医学文献。PMID 通常存储在文献的 'extra'
    字段中，格式为 'PMID: 12345678'。

    Args:
        pmid: PubMed ID 字符串

    Returns:
        List[Dict]: 匹配的文献列表

    Raises:
        ZoteroLocalError: 当搜索失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> results = client.search_by_pmid("12345678")
        >>> for item in results:
        ...     print(item['data']['title'])

    Note:
        PMID 存储在文献的 extra 字段中
        搜索会在 extra 字段的每一行中查找 'PMID: {pmid}' 模式
        主要用于医学和生物医学文献
    """
```

### search_by_title()

```python
def search_by_title(self, title: str, exact_match: bool = False) -> List[Dict]:
    """
    通过标题搜索文献

    根据文献标题进行搜索，支持精确匹配和模糊匹配。
    搜索不区分大小写。

    Args:
        title: 要搜索的标题文本
        exact_match: 是否精确匹配。True 表示只返回完全匹配的结果，
                    False 表示包含关键词即可（默认）

    Returns:
        List[Dict]: 匹配的文献条目列表

    Raises:
        ZoteroLocalError: 当搜索失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> # 模糊搜索标题包含 "深度学习" 的文献
        >>> results = client.search_by_title("深度学习")
        >>> print(f"找到 {len(results)} 篇相关文献")

        >>> # 精确搜索标题为 "机器学习基础" 的文献
        >>> results = client.search_by_title("机器学习基础", exact_match=True)
        >>> if results:
        ...     print(f"找到完全匹配的文献: {results[0]['data']['title']}")

    Note:
        搜索不区分大小写
        exact_match=False 时使用包含匹配
        exact_match=True 时使用完全相等匹配
    """
```

## 实现细节

### 搜索算法

`SearchMixin` 使用以下搜索策略：

1. **关键词搜索** (`search_items`)
   - 直接使用 Zotero API 的搜索参数
   - 利用 Zotero 服务端的搜索功能

2. **DOI 搜索** (`search_by_doi`)
   ```python
   def search_by_doi(self, doi: str) -> List[Dict]:
       items = self.get_items()  # 获取所有文献
       matching_items = [
           item for item in items
           if item.get('data', {}).get('DOI', '').lower() == doi.lower()
       ]
       return matching_items
   ```

3. **PMID 搜索** (`search_by_pmid`)
   ```python
   def search_by_pmid(self, pmid: str) -> List[Dict]:
       items = self.get_items()
       matching_items = []

       for item in items:
           extra = item.get('data', {}).get('extra', '')
           if extra:
               for line in extra.split('\n'):
                   if line.startswith('PMID:') and line.split(':')[1].strip() == pmid:
                       matching_items.append(item)
                       break
       return matching_items
   ```

4. **标题搜索** (`search_by_title`)
   ```python
   def search_by_title(self, title: str, exact_match: bool = False):
       items = self.get_items()

       for item in items:
           item_title = item.get('data', {}).get('title', '').lower()
           search_title = title.lower()

           if exact_match:
               if item_title == search_title:
                   matching_items.append(item)
           else:
               if search_title in item_title:
                   matching_items.append(item)
   ```

### 性能考虑

- `search_items()` 使用 Zotero API 服务端搜索，性能较好
- `search_by_doi()`, `search_by_pmid()`, `search_by_title()` 需要获取所有文献后在本地筛选，对于大型文献库可能较慢
- 建议对大型文献库使用分页或缓存策略

## 扩展示例

### 高级搜索功能

```python
class AdvancedSearchMixin(SearchMixin):
    """扩展的搜索功能 Mixin"""

    def search_by_author(self, author_name: str) -> List[Dict]:
        """按作者姓名搜索"""
        items = self.get_items()
        matching_items = []

        for item in items:
            creators = item.get('data', {}).get('creators', [])
            for creator in creators:
                if creator.get('creatorType') == 'author':
                    full_name = f"{creator.get('firstName', '')} {creator.get('lastName', '')}".lower()
                    if author_name.lower() in full_name:
                        matching_items.append(item)
                        break

        return matching_items

    def search_by_year(self, year: str) -> List[Dict]:
        """按发表年份搜索"""
        import re
        items = self.get_items()
        matching_items = []

        for item in items:
            date = item.get('data', {}).get('date', '')
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            if year_match and year_match.group() == year:
                matching_items.append(item)

        return matching_items

    def search_by_publication(self, venue: str) -> List[Dict]:
        """按期刊/会议名称搜索"""
        items = self.get_items()
        matching_items = []

        for item in items:
            publication = item.get('data', {}).get('publicationTitle', '')
            if venue.lower() in publication.lower():
                matching_items.append(item)

        return matching_items

    def advanced_search(self,
                       query: str = None,
                       author: str = None,
                       year: str = None,
                       venue: str = None,
                       item_type: str = None) -> List[Dict]:
        """高级多条件搜索"""
        all_items = self.get_items()
        matching_items = []

        for item in all_items:
            data = item.get('data', {})
            match = True

            # 关键词搜索
            if query:
                title = data.get('title', '').lower()
                abstract = data.get('abstractNote', '').lower()
                if not (query.lower() in title or query.lower() in abstract):
                    match = False

            # 作者搜索
            if author and match:
                creators = data.get('creators', [])
                author_found = False
                for creator in creators:
                    if creator.get('creatorType') == 'author':
                        creator_name = f"{creator.get('firstName', '')} {creator.get('lastName', '')}".lower()
                        if author.lower() in creator_name:
                            author_found = True
                            break
                if not author_found:
                    match = False

            # 年份搜索
            if year and match:
                date = data.get('date', '')
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', date)
                if not (year_match and year_match.group() == year):
                    match = False

            # 期刊搜索
            if venue and match:
                publication = data.get('publicationTitle', '').lower()
                if venue.lower() not in publication:
                    match = False

            # 类型搜索
            if item_type and match:
                current_type = data.get('itemType', '')
                if item_type.lower() != current_type.lower():
                    match = False

            if match:
                matching_items.append(item)

        return matching_items

    def search_with_fuzzy_matching(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """模糊匹配搜索"""
        from difflib import SequenceMatcher

        items = self.get_items()
        matching_items = []

        for item in items:
            title = item.get('data', {}).get('title', '')
            similarity = SequenceMatcher(None, query.lower(), title.lower()).ratio()

            if similarity >= threshold:
                item_copy = item.copy()
                item_copy['_similarity'] = similarity
                matching_items.append(item_copy)

        # 按相似度排序
        matching_items.sort(key=lambda x: x['_similarity'], reverse=True)
        return matching_items
```

### 使用扩展搜索

```python
class ExtendedZoteroClient(ZoteroLocal, AdvancedSearchMixin):
    """扩展的 Zotero 客户端"""
    pass

# 使用扩展功能
client = ExtendedZoteroClient()

# 按作者搜索
author_results = client.search_by_author("Goodfellow")

# 按年份搜索
year_results = client.search_by_year("2023")

# 高级多条件搜索
advanced_results = client.advanced_search(
    query="machine learning",
    author="Goodfellow",
    year="2016",
    venue="NIPS"
)

# 模糊搜索
fuzzy_results = client.search_with_fuzzy_matching("deep learning", threshold=0.7)
```

## 搜索建议和最佳实践

### 1. 搜索策略

```python
def smart_search(query: str) -> List[Dict]:
    """智能搜索策略"""
    client = ZoteroLocal()

    # 首先尝试 DOI 搜索
    if query.startswith('10.'):
        doi_results = client.search_by_doi(query)
        if doi_results:
            return doi_results

    # 然后尝试 PMID 搜索
    if query.isdigit() and len(query) == 8:
        pmid_results = client.search_by_pmid(query)
        if pmid_results:
            return pmid_results

    # 最后进行关键词搜索
    return client.search_items(query)
```

### 2. 结果排序和过滤

```python
def sort_search_results(results: List[Dict], sort_by: str = 'year') -> List[Dict]:
    """排序搜索结果"""
    if sort_by == 'year':
        def extract_year(item):
            date = item['data'].get('date', '')
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            return int(year_match.group()) if year_match else 0
        return sorted(results, key=extract_year, reverse=True)

    elif sort_by == 'title':
        return sorted(results, key=lambda x: x['data'].get('title', '').lower())

    elif sort_by == 'relevance':
        # 简单的相关性排序（可以根据需要实现更复杂的算法）
        return results

    return results
```

### 3. 搜索缓存

```python
from functools import lru_cache
import hashlib

class CachedSearchMixin(SearchMixin):
    """带缓存的搜索 Mixin"""

    @lru_cache(maxsize=100)
    def _cached_search_items(self, query_hash: str) -> List[Dict]:
        """缓存的搜索方法"""
        # 注意：这里需要实际的实现
        # 由于 lru_cache 参数必须是可哈希的，需要特殊处理
        pass

    def search_items_cached(self, query: str) -> List[Dict]:
        """带缓存的搜索"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return self._cached_search_items(query_hash)
```

## 注意事项

1. **性能**: `search_by_doi()`, `search_by_pmid()`, `search_by_title()` 需要获取所有文献后在本地处理，对于大型文献库可能较慢
2. **大小写**: 所有搜索方法都不区分大小写
3. **返回格式**: 所有搜索方法返回相同的数据结构，与 Zotero API 响应格式一致
4. **错误处理**: 所有搜索方法都可能抛出 `ZoteroLocalError`
5. **网络依赖**: 除了本地筛选的搜索方法，其他搜索都需要网络连接到 Zotero 服务器

`SearchMixin` 提供了灵活多样的搜索功能，满足不同场景下的文献查找需求。