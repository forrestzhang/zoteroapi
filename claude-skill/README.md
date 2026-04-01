# ZoteroAPI Claude Skill

Claude Code 技能扩展，提供便捷的命令行工具和 Python API 来搜索和导出 Zotero 本地库中的文献。

## 文件说明

```
claude-skill/
├── SKILL.md              # 技能完整文档
├── scripts/              # 实用脚本
│   ├── zotero_search.py      # 通用搜索工具 (PMID/DOI/关键词/标题)
│   ├── query_by_pmid.py      # PMID 查询工具
│   ├── batch_export.py       # 批量导出 PDF
│   ├── test_connection.py    # 连接测试
│   └── test_search.py        # 搜索测试
└── README.md             # 本文件
```

## 安装方法

### 方法一：作为 Claude Code 技能安装（推荐）

```bash
ln -s /Users/forrest/GitHub/zoteroapi/claude-skill \
  ~/.claude/skills/zoteroapi
```

### 方法二：直接使用脚本

```bash
# 搜索文献
python3 /Users/forrest/GitHub/zoteroapi/claude-skill/scripts/zotero_search.py \
  --pmid 39659015 --output result.json

# 批量导出 PDF
python3 /Users/forrest/GitHub/zoteroapi/claude-skill/scripts/batch_export.py \
  "My Collection" /path/to/output
```

## 依赖

- Python 3.8+
- `zoteroapi` 包（本库）
- `tabulate`（可选，用于表格输出）

## 特性

- ✅ 支持新版 Zotero（独立 PMID 字段）和旧版（extra 字段）
- ✅ 按 PMID、DOI、关键词、标题搜索
- ✅ 批量导出 PDF
- ✅ JSON/Markdown/表格多种输出格式

## 使用示例

```bash
# 按 PMID 搜索
python3 scripts/zotero_search.py --pmid 39659015

# 按关键词搜索
python3 scripts/zotero_search.py --search "machine learning" --limit 10

# 批量查询 PMID
python3 scripts/query_by_pmid.py 39659015 38877035 --format markdown

# 导出集合 PDF
python3 scripts/batch_export.py "My Collection" ~/Downloads/papers
```

## Python API

```python
import sys
sys.path.insert(0, "/Users/forrest/GitHub/zoteroapi/claude-skill/scripts")

from zotero_search import ZoteroSearch

searcher = ZoteroSearch()
results = searcher.search_by_pmid("39659015")
```
