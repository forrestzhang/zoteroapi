# 搜索功能示例

本文档展示了 ZoteroAPI 的各种搜索功能和使用场景。

## 基础搜索

### 关键词搜索

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# 基础关键词搜索
results = client.search_items("深度学习")
print(f"找到 {len(results)} 篇包含 '深度学习' 的文献")

# 搜索短语（使用引号）
phrase_results = client.search_items('"machine learning"')
print(f"找到 {len(phrase_results)} 篇包含短语的文献")

# 多关键词搜索（会搜索包含任一关键词的文献）
multi_results = client.search_items("深度 learning neural")
print(f"找到 {len(multi_results)} 篇相关文献")
```

### DOI 精确搜索

```python
# 通过 DOI 搜索文献
doi_list = [
    "10.1038/nature12373",
    "10.1126/science.1258050",
    "10.1109/5.771073"
]

for doi in doi_list:
    results = client.search_by_doi(doi)
    if results:
        item = results[0]
        title = item['data']['title']
        authors = ', '.join([f"{c['lastName']}, {c['firstName'][0]}"
                           for c in item['data'].get('creators', [])[:3]])
        print(f"DOI: {doi}")
        print(f"标题: {title}")
        print(f"作者: {authors}")
        print("-" * 40)
    else:
        print(f"未找到 DOI: {doi}")
```

### PubMed ID 搜索

```python
# 搜索医学文献
pmid_list = ["12345678", "87654321", "11223344"]

for pmid in pmid_list:
    results = client.search_by_pmid(pmid)
    if results:
        item = results[0]
        title = item['data']['title']
        journal = item['data'].get('publicationTitle', '未知期刊')
        year = item['data'].get('date', '未知年份')
        print(f"PMID: {pmid}")
        print(f"标题: {title}")
        print(f"期刊: {journal} ({year})")
        print("-" * 40)
    else:
        print(f"未找到 PMID: {pmid}")
```

### 标题搜索

```python
# 模糊搜索标题
fuzzy_results = client.search_by_title("machine learning")
print(f"标题包含 'machine learning' 的文献: {len(fuzzy_results)} 篇")

# 精确搜索标题
exact_results = client.search_by_title("Machine Learning", exact_match=True)
print(f"标题完全匹配 'Machine Learning' 的文献: {len(exact_results)} 篇")

# 搜索标题包含特定词汇的文献
keywords = ["introduction", "survey", "review", "tutorial"]

for keyword in keywords:
    results = client.search_by_title(keyword)
    print(f"'{keyword}': {len(results)} 篇")
```

## 高级搜索技巧

### 按作者搜索

```python
def search_by_author(author_name):
    """按作者姓名搜索文献"""
    all_items = client.get_items()
    matching_items = []

    for item in all_items:
        creators = item.get('data', {}).get('creators', [])
        for creator in creators:
            if creator.get('creatorType') == 'author':
                last_name = creator.get('lastName', '').lower()
                first_name = creator.get('firstName', '').lower()
                full_name = f"{first_name} {last_name}".lower()

                if author_name.lower() in full_name:
                    matching_items.append(item)
                    break

    return matching_items

# 搜索特定作者的文献
author_results = search_by_author("Goodfellow")
print(f"Goodfellow 的文献: {len(author_results)} 篇")

for item in author_results[:5]:
    title = item['data']['title']
    print(f"- {title}")
```

### 按发表年份搜索

```python
def search_by_year(year):
    """按发表年份搜索文献"""
    all_items = client.get_items()
    matching_items = []

    for item in all_items:
        date = item.get('data', {}).get('date', '')
        # 尝试提取年份
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', date)
        if year_match and year_match.group() == year:
            matching_items.append(item)

    return matching_items

# 搜索特定年份的文献
year = 2023
year_results = search_by_year(str(year))
print(f"{year} 年的文献: {len(year_results)} 篇")
```

### 按期刊/会议搜索

```python
def search_by_publication(venue_name):
    """按期刊或会议名称搜索"""
    all_items = client.get_items()
    matching_items = []

    for item in all_items:
        publication = item.get('data', {}).get('publicationTitle', '').lower()
        if venue_name.lower() in publication:
            matching_items.append(item)

    return matching_items

# 搜索特定期刊的文献
journals = ["Nature", "Science", "Cell", "NeurIPS", "ICML"]

for journal in journals:
    results = search_by_publication(journal)
    print(f"{journal}: {len(results)} 篇")
```

## 组合搜索

### 多条件搜索

```python
def advanced_search(query=None, author=None, year=None, venue=None):
    """高级多条件搜索"""
    all_items = client.get_items()
    matching_items = []

    for item in all_items:
        data = item.get('data', {})
        match = True

        # 标题/摘要/关键词搜索
        if query:
            title = data.get('title', '').lower()
            abstract = data.get('abstractNote', '').lower()
            tags = [tag.get('tag', '').lower() for tag in data.get('tags', [])]

            if not (query.lower() in title or
                   query.lower() in abstract or
                   any(query.lower() in tag for tag in tags)):
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

        # 期刊/会议搜索
        if venue and match:
            publication = data.get('publicationTitle', '').lower()
            if venue.lower() not in publication:
                match = False

        if match:
            matching_items.append(item)

    return matching_items

# 使用组合搜索
results = advanced_search(
    query="machine learning",
    author="Goodfellow",
    year="2016"
)

print(f"Goodfellow 在 2016 年关于机器学习的文献: {len(results)} 篇")
```

## 搜索结果处理

### 结果排序

```python
def sort_results(results, sort_by='title', reverse=False):
    """对搜索结果进行排序"""
    if sort_by == 'title':
        return sorted(results,
                     key=lambda x: x['data'].get('title', ''),
                     reverse=reverse)
    elif sort_by == 'year':
        def extract_year(item):
            date = item['data'].get('date', '')
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            return int(year_match.group()) if year_match else 0

        return sorted(results, key=extract_year, reverse=reverse)
    elif sort_by 'author':
        def get_first_author(item):
            creators = item['data'].get('creators', [])
            for creator in creators:
                if creator.get('creatorType') == 'author':
                    return f"{creator.get('lastName', '')} {creator.get('firstName', '')}"
            return ''

        return sorted(results, key=get_first_author, reverse=reverse)
    else:
        return results

# 对搜索结果进行排序
search_results = client.search_items("deep learning")

# 按标题排序
sorted_by_title = sort_results(search_results, 'title')

# 按年份降序排序
sorted_by_year = sort_results(search_results, 'year', reverse=True)

print("按年份排序的最新文献：")
for item in sorted_by_year[:5]:
    title = item['data']['title']
    year = item['data'].get('date', '')
    print(f"- {title} ({year})")
```

### 结果去重

```python
def remove_duplicates(results):
    """去除重复的搜索结果"""
    seen_titles = set()
    unique_results = []

    for item in results:
        title = item['data'].get('title', '').lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_results.append(item)

    return unique_results

# 去重示例
all_results = []
queries = ["machine learning", "深度学习", "artificial intelligence"]

for query in queries:
    results = client.search_items(query)
    all_results.extend(results)

# 去重
unique_results = remove_duplicates(all_results)
print(f"去重前: {len(all_results)} 篇, 去重后: {len(unique_results)} 篇")
```

## 搜索统计和分析

### 搜索趋势分析

```python
def analyze_search_terms(terms):
    """分析搜索词的热度"""
    analysis = {}

    for term in terms:
        results = client.search_items(term)
        analysis[term] = len(results)

    # 按结果数量排序
    sorted_analysis = sorted(analysis.items(), key=lambda x: x[1], reverse=True)

    print("搜索词热度分析：")
    for term, count in sorted_analysis:
        print(f"'{term}': {count} 篇")

    return sorted_analysis

# 分析热点词汇
hot_topics = [
    "machine learning",
    "deep learning",
    "neural networks",
    "transformer",
    "attention mechanism",
    "reinforcement learning",
    "natural language processing",
    "computer vision"
]

trend_analysis = analyze_search_terms(hot_topics)
```

### 搜索结果质量评估

```python
def assess_search_quality(results, query):
    """评估搜索结果质量"""
    if not results:
        return 0

    # 计算标题匹配度
    title_matches = sum(1 for item in results
                       if query.lower() in item['data'].get('title', '').lower())

    # 计算摘要匹配度
    abstract_matches = sum(1 for item in results
                          if query.lower() in item['data'].get('abstractNote', '').lower())

    # 计算相关度分数
    total_items = len(results)
    title_score = title_matches / total_items * 0.5
    abstract_score = abstract_matches / total_items * 0.3
    tag_score = 0.2  # 假设所有结果都有相关标签

    quality_score = (title_score + abstract_score + tag_score) * 100

    print(f"搜索 '{query}' 的质量评估：")
    print(f"  标题匹配: {title_matches}/{total_items} ({title_score*100:.1f}%)")
    print(f"  摘要匹配: {abstract_matches}/{total_items} ({abstract_score*100:.1f}%)")
    print(f"  总体质量: {quality_score:.1f}/100")

    return quality_score

# 评估搜索质量
search_results = client.search_items("deep learning")
quality = assess_search_quality(search_results, "deep learning")
```

## 实用搜索工具

### 智能搜索建议

```python
def suggest_search_improvements(query):
    """提供搜索改进建议"""
    suggestions = []

    # 检查查询长度
    if len(query) < 3:
        suggestions.append("搜索词太短，建议使用更具体的关键词")

    # 检查是否包含常见缩写
    abbreviations = {
        'ml': 'machine learning',
        'dl': 'deep learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'cv': 'computer vision'
    }

    query_lower = query.lower()
    for abbr, full in abbreviations.items():
        if abbr == query_lower:
            suggestions.append(f"尝试使用完整词汇: '{full}'")
        elif abbr in query_lower:
            suggestions.append(f"考虑将 '{abbr}' 替换为 '{full}'")

    # 建议相关搜索词
    related_terms = {
        'neural': ['network', 'networks', 'deep', 'artificial'],
        'learning': ['machine', 'deep', 'reinforcement', 'supervised'],
        'vision': ['computer', 'image', 'object detection', 'segmentation']
    }

    for key, terms in related_terms.items():
        if key in query_lower:
            suggestions.append(f"相关搜索词: {', '.join(terms[:3])}")

    return suggestions

# 获取搜索建议
user_query = "ml"
improvements = suggest_search_improvements(user_query)

if improvements:
    print("搜索改进建议：")
    for suggestion in improvements:
        print(f"  • {suggestion}")
else:
    print("搜索词看起来不错！")
```

### 批量搜索

```python
def batch_search(queries, max_results_per_query=10):
    """批量搜索多个关键词"""
    all_results = {}

    for query in queries:
        try:
            results = client.search_items(query)
            limited_results = results[:max_results_per_query]
            all_results[query] = limited_results
            print(f"'{query}': {len(limited_results)} 篇文献")
        except Exception as e:
            print(f"搜索 '{query}' 时出错: {e}")
            all_results[query] = []

    return all_results

# 批量搜索示例
research_topics = [
    "transformer architecture",
    "bert model",
    "gpt",
    "attention mechanism"
]

batch_results = batch_search(research_topics)

# 汇总结果
total_unique = len(set(
    item['key'] for results in batch_results.values()
    for item in results
))
print(f"\n总计找到 {total_unique} 篇唯一文献")
```

## 小结

- 使用 `search_items()` 进行关键词搜索
- 使用 `search_by_doi()` 和 `search_by_pmid()` 进行精确搜索
- 使用 `search_by_title()` 进行标题搜索
- 实现自定义的多条件搜索函数
- 对结果进行排序、去重和质量评估
- 使用工具函数优化搜索体验

这些技巧可以帮助你更有效地找到所需的文献。