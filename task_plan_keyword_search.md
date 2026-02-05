# Task Plan: Zotero 关键词搜索与数据导出

**Created:** 2026-01-29
**Status:** In Progress

## Goal

使用 zoteroapi 进行关键词搜索，将搜索结果导出为结构化数据（JSON），供其他工具使用。

## 用户需求

- 输入：关键词（搜索查询）
- 输出：结构化数据（JSON 格式）
  - 包含论文的完整信息
  - 可以被其他工具/脚本解析和使用
- 使用场景：作为数据源为其他工具提供论文信息

## Phase 1: 需求分析与设计 (Complete)

**Objectives:**
- 分析现有搜索功能
- 确定数据输出格式
- 设计与现有脚本的集成方式

**Status:** Complete

**Decisions:**
- **实现方式**: 创建通用工具脚本 `zotero_search.py`
- **使用场景**: 支持命令行和 Python API 两种方式
- **输出格式**: 与 `query_by_pmid.py` 的 JSON 格式保持一致
- **功能范围**: 基础搜索导出（PMID、DOI、关键词、标题）

**Deliverables:**
- 功能需求文档 ✓
- 数据格式设计 ✓
- 集成方案 ✓

---

## Phase 2: 实现 zotero_search.py (Complete)

**Status:** Complete

**Objectives:**
- 创建通用工具脚本 `zotero_search.py`
- 支持多种搜索方式（PMID、DOI、关键词、标题）
- 确保命令行和 Python API 都可以使用
- 确保 JSON 输出格式标准化

**Design:**

```bash
# 命令行使用
python zotero_search.py --pmid 12345678 --output results.json
python zotero_search.py --doi "10.1038/nature12373" --output results.json
python zotero_search.py --search "machine learning" --output results.json
python zotero_search.py --title "Deep Learning" --output results.json

# Python API 使用
from zotero_search import ZoteroSearch
searcher = ZoteroSearch()
results = searcher.search_by_keyword("machine learning")
```

**Deliverables:**
- `~/.claude/skills/zoteroapi/scripts/zotero_search.py` 脚本 ✓

**Errors:** None

**Testing:**
- ✓ 命令行关键词搜索
- ✓ Python API 关键词搜索

---

## Phase 3: 测试与验证 (Complete)

**Status:** Complete

**Objectives:**
- 测试所有搜索方法
- 验证 JSON 输出格式
- 测试与其他工具的集成

**Deliverables:**
- 测试结果 ✓
- 使用示例 ✓

**Testing Results:**
- ✓ PMID 搜索（命令行 + Python API）
- ✓ DOI 搜索（命令行 + Python API）
- ✓ 关键词搜索（命令行 + Python API）
- ✓ 标题搜索（命令行 + Python API）
- ✓ JSON 文件输出
- ✓ JSON stdout 输出
- ✓ limit 参数功能
- ✓ exact_match 参数功能

**Errors:** None

---

## Phase 4: 文档更新 (Complete)

**Objectives:**
- 更新 zoteroapi skill.md 文档
- 添加 zotero_search.py 使用说明
- 提供集成示例

**Status:** Complete

**Deliverables:**
- 更新的 skill.md 文档 ✓

**Changes Made:**
1. 在 Main Scripts 表格中添加了 `zotero_search.py`
2. 添加了完整的 Universal Search Script 文档部分
3. 添加了 4 个新的 Example Interactions

**Errors:** None

---

## Phase 3: 测试与验证

**Status:** Pending

**Objectives:**
- 测试关键词搜索功能
- 验证 JSON 输出格式
- 测试与其他工具的集成

**Deliverables:**
- 测试结果
- 使用示例

---

## Options

### 实现方式
- **Option 1**: 新脚本 `search_and_export.py` - 专门用于搜索和导出
- **Option 2**: 扩展 `query_by_pmid.py` - 添加关键词搜索功能
- **Option 3**: 通用工具脚本 - 统一的搜索接口

### 输出格式
- **Option 1**: 仅 JSON（最适合工具集成）
- **Option 2**: 多种格式（与 query_by_pmid.py 一致）

## Decision Log

### 待决策
- [ ] 实现方式选择
- [ ] 输出格式选择
- [ ] 是否需要支持批量搜索

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| None | - | - |

## Next Steps

1. 分析现有功能
2. 设计数据格式
3. 选择实现方案
4. 实现功能
5. 测试验证
