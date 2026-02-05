# Task Plan: PMID 查询与论文信息导出

**Created:** 2026-01-29
**Status:** In Progress

## Goal

使用 zoteroapi 通过 PMID 查询 Zotero 本地库中的论文，并输出论文的详细信息（标题、作者、期刊、DOI、摘要等）。

## 用户需求

- 输入：PMID（可以是一个或多个）
- 输出：论文的完整信息
  - 标题
  - 作者
  - 期刊
  - 发表日期
  - DOI
  - 摘要
  - 标签
  - 附件信息

## Phase 1: 需求分析与设计 (Complete)

**Objectives:**
- 确定 PMID 查询的工作流程
- 设计输出格式
- 规划脚本功能

**Deliverables:**
- 功能需求文档
- 脚本设计

**Status:** Complete

**Decisions:**
- 创建一个新的脚本 `query_by_pmid.py`
- 支持单个 PMID 和批量 PMID 查询
- 输出格式支持：表格、JSON、Markdown
- 使用 tabulate 库实现表格输出

**Errors:** None

---

## Phase 2: 实现 PMID 查询脚本 (Complete)

**Objectives:**
- 实现 `query_by_pmid.py` 脚本
- 支持多种输出格式
- 添加错误处理

**Deliverables:**
- `~/.claude/skills/zoteroapi/scripts/query_by_pmid.py`

**Status:** Complete

**Decisions:**
- 支持命令行参数输入 PMID
- 支持从文件读取 PMID 列表
- 输出格式：table（默认）、json、markdown
- 添加了 verbose 选项显示摘要和标签

**Errors:** None

---

## Phase 3: 测试与验证 (Complete)

**Objectives:**
- 测试单个 PMID 查询
- 测试批量 PMID 查询
- 验证输出格式

**Deliverables:**
- 测试结果

**Status:** Complete

**Decisions:**
- 安装了 `tabulate` 库以支持表格输出

**Errors:**
| Error | Attempt | Resolution |
|-------|---------|------------|
| 作者显示为空/Null | 1 | 修复 `format_authors()` 函数，支持 `firstName` + `lastName` 字段 |
| JSON 输出作者为 Null | 2 | 修复 `output_json()` 函数中的作者提取逻辑 |

**测试结果:**
- ✓ 单个 PMID 查询（表格格式）
- ✓ 多个 PMID 查询（表格格式）
- ✓ Verbose 输出（包含摘要、标签、附件信息）
- ✓ Markdown 格式输出
- ✓ JSON 格式输出
- ✓ JSON 输出到文件

---

## Phase 4: 文档更新 (Pending - Optional)

**Objectives:**
- 更新 skill.md 文档
- 添加使用示例

**Deliverables:**
- 更新的文档

**Status:** Pending (Optional - 可以在需要时更新)

**Errors:** None

---

## Options

### 输出格式
- **Option 1**: 表格格式（易读）
- **Option 2**: JSON 格式（易解析）
- **Option 3**: Markdown 格式（文档友好）
- **Option 4**: 支持所有格式

### 功能范围
- **Option 1**: 仅查询基本信息
- **Option 2**: 查询所有可用信息（包括附件、标签等）

## Decision Log

### 输出格式选择
**Date:** 2026-01-29
**Decision:** 支持多种输出格式（表格、JSON、Markdown）
**Rationale:** 不同场景需要不同格式
**Revisit:** 如有新的格式需求

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| None | - | - |

## Next Steps

1. 完成 Phase 1：确定详细需求
2. 实现 Phase 2：创建 `query_by_pmid.py` 脚本
3. 测试 Phase 3：验证功能
