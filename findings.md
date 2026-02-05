# Findings: PMID 查询与论文信息导出

**Created:** 2026-01-29

## zoteroapi 现有功能

### PMID 搜索功能
- `search_by_pmid(pmid: str)` - 在 Zotero 本地库中搜索 PMID
- PMID 存储在项目的 `extra` 字段中，格式为 `PMID: xxxxxxxx`
- 返回匹配的项目列表

### 项目数据结构

```python
{
    'key': 'ABC123XYZ',
    'version': 1234,
    'data': {
        'title': 'Paper Title',
        'creators': [
            {'creatorType': 'author', 'name': 'Author Name'},
            # ...
        ],
        'abstractNote': 'Abstract text',
        'publicationTitle': 'Journal Name',
        'volume': '10',
        'issue': '1',
        'pages': '1-10',
        'date': '2024',
        'DOI': '10.1234/example',
        'extra': 'PMID: 12345678\nOther info',
        'tags': [{'tag': 'keyword1'}, {'tag': 'keyword2'}],
        'itemType': 'journalArticle'
    },
    'meta': {
        'createdByUser': {'id': 1, 'name': 'User'},
        'numChildren': 1  # 附件数量
    },
    'links': {
        'attachment': {
            'href': 'http://localhost:23119/api/users/14810854/items/ATTACHMENT_KEY',
            'type': 'application/json',
            'attachmentType': 'application/pdf'
        }
    }
}
```

## 脚本设计要点

### 输入方式
1. 命令行参数：单个 PMID
2. 命令行参数：多个 PMID
3. 文件输入：PMID 列表文件
4. 交互式输入

### 输出格式
1. **表格格式**：使用 `tabulate` 库或类似工具
2. **JSON 格式**：结构化数据，易于解析
3. **Markdown 格式**：适合文档和笔记

### 功能需求
- [ ] 支持单个 PMID 查询
- [ ] 支持批量 PMID 查询
- [ ] 支持从文件读取 PMID 列表
- [ ] 输出多种格式
- [ ] 错误处理（PMID 不存在等）
- [ ] 显示附件信息

## 待解决问题

1. 是否需要处理 PMID 不存在于本地库的情况？
2. 是否需要提示用户添加缺失的 PMID？
3. 输出字段如何定制化？
