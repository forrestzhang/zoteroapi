# Findings: Zotero 关键词搜索与数据导出

**Created:** 2026-01-29

## 现有 zoteroapi 搜索功能

### search_items(query: str)
根据关键词搜索 Zotero 库中的项目。

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
results = client.search_items("machine learning")
```

**特点:**
- 在标题、作者、摘要等字段中搜索
- 返回匹配的项目列表
- 返回结果与 `get_items()` 相同的数据结构

## 现有脚本分析

### query_by_pmid.py
- **输入**: PMID（命令行参数或文件）
- **输出格式**: table、json、markdown
- **JSON 输出结构**:

```json
[
  {
    "pmid": "39122952",
    "key": "ABC123XYZ",
    "title": "Paper Title",
    "authors": ["Author1", "Author2"],
    "abstract": "Abstract text",
    "journal": "Journal Name",
    "volume": "10",
    "issue": "1",
    "pages": "1-10",
    "date": "2024",
    "doi": "10.1234/example",
    "tags": ["tag1", "tag2"],
    "has_attachment": true,
    "item_type": "journalArticle"
  }
]
```

## 设计考虑

### 数据格式一致性
与 `query_by_pmid.py` 的 JSON 输出保持一致有以下好处：
1. 统一的数据接口
2. 现有工具可以无缝使用
3. 降低维护成本

### 扩展 vs 新脚本

**扩展 query_by_pmid.py 的优点:**
- 统一的接口
- 代码复用
- 已有的输出格式支持

**扩展 query_by_pmid.py 的缺点:**
- 脚本名称可能引起混淆（query_by_pmid 但支持关键词搜索）

**新脚本的优点:**
- 更清晰的命名
- 可以针对关键词搜索优化
- 不影响现有功能

**新脚本的缺点:**
- 代码重复
- 需要维护多个脚本

### 集成方案

**方案 1: 扩展 query_by_pmid.py**
```bash
# 添加 --search 或 -s 选项
python query_by_pmid.py --search "machine learning" --format json --output results.json
```

**方案 2: 新脚本 search_and_export.py**
```bash
python search_and_export.py "machine learning" --output results.json
```

**方案 3: 通用工具脚本 zotero_search.py**
```bash
# 支持多种搜索方式
python zotero_search.py --pmid 12345678 --output results.json
python zotero_search.py --doi "10.1038/nature12373" --output results.json
python zotero_search.py --search "machine learning" --output results.json
python zotero_search.py --title "Deep Learning" --output results.json
```

## 实现结果

### zotero_search.py 脚本

创建位置: `~/.claude/skills/zoteroapi/scripts/zotero_search.py`

**功能特性:**
1. 支持四种搜索模式：PMID、DOI、关键词、标题
2. 同时支持命令行和 Python API 两种使用方式
3. JSON 输出格式与 `query_by_pmid.py` 保持一致
4. 支持结果限制（`--limit` / `limit` 参数）
5. 支持精确标题匹配（`--exact` / `exact_match` 参数）
6. 可输出到文件或 stdout

**数据格式一致性:**
与 `query_by_pmid.py` 输出完全相同的 JSON 结构，确保：
- 统一的数据接口
- 现有工具可以无缝使用
- 降低维护成本

### 与其他工具的集成

**管道处理:**
```bash
# 搜索结果传递给其他工具
python zotero_search.py --search "machine learning" --no-pretty | \
    jq '.[] | .title, .authors'
```

**Python 中导入:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('~/.claude/skills/zoteroapi/scripts').expanduser()))
from zotero_search import ZoteroSearch
```

## 待解决的问题

1. 是否需要支持高级搜索（组合条件、布尔运算）？
2. 结果排序方式（相关性、日期、期刊）？
3. 结果数量限制？（已实现基础 limit 功能）
4. 是否需要分页处理大量结果？
