# 笔记管理

本页面介绍如何使用 ZoteroAPI 管理文献笔记。

## 添加笔记

为文献条目添加笔记：

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# 获取一篇文献
items = client.get_items_top(limit=1)
item_key = items[0]['key']

# 添加笔记
note = client.add_item_note(
    item_key=item_key,
    note_text="这是一篇很有价值的论文，提出了创新性的方法。",
    title="阅读笔记"  # 可选
)

print(f"✅ 笔记已添加，Key: {note['key']}")
```

**参数说明**：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| item_key | str | 是 | 要添加笔记的文献条目 key |
| note_text | str | 是 | 笔记内容（支持 HTML） |
| title | str | 否 | 笔记标题 |

**返回值**：创建的笔记对象

!!! tip "笔记格式"
    笔记内容支持 HTML 格式，可以包含格式化文本、链接等。

## 获取笔记

### 获取单个笔记

通过 note_key 获取特定笔记：

```python
# 假设已知笔记的 key
note_key = "NOTE123"

try:
    note = client.get_note(note_key)
    
    # 提取笔记信息
    data = note.get('data', {})
    note_content = data.get('note', '')
    parent_item = data.get('parentItem', '')
    
    print(f"笔记内容: {note_content}")
    print(f"所属文献: {parent_item}")
except ZoteroLocalError as e:
    print(f"获取笔记失败: {e}")
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| note_key | str | 笔记的唯一标识符 |

**返回值**：笔记对象

### 获取文献的所有笔记

获取某篇文献的所有笔记：

```python
# 获取文献的所有笔记
item_key = "ABC123"
notes = client.get_item_notes(item_key)

print(f"该文献有 {len(notes)} 条笔记：\n")

for i, note in enumerate(notes, 1):
    data = note.get('data', {})
    content = data.get('note', '')
    # 去除 HTML 标签显示（简单处理）
    plain_text = content.replace('<p>', '').replace('</p>', '\n')
    print(f"{i}. {plain_text[:100]}...")  # 显示前 100 个字符
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| item_key | str | 文献条目的 key |

**返回值**：笔记对象列表

## 笔记数据结构

笔记对象包含以下字段：

```python
{
    "key": "NOTE123",
    "version": 45,
    "library": {...},
    "links": {...},
    "meta": {
        "createdByUser": {...},
        "createdDate": "2024-01-15T10:30:00Z",
        "lastModifiedByUser": {...},
        "lastModifiedDate": "2024-01-15T14:20:00Z",
        "numChildren": 0
    },
    "data": {
        "key": "NOTE123",
        "version": 45,
        "itemType": "note",
        "parentItem": "ABC123",  # 所属文献的 key
        "note": "<p>笔记内容（HTML格式）</p>",
        "tags": [],
        "collections": [],
        "relations": {}
    }
}
```

### 关键字段

| 字段路径 | 说明 |
|----------|------|
| `data.note` | 笔记内容（HTML 格式） |
| `data.parentItem` | 所属文献的 key |
| `data.tags` | 笔记的标签 |
| `meta.createdDate` | 创建时间 |
| `meta.lastModifiedDate` | 最后修改时间 |

## HTML 格式笔记

### 创建格式化笔记

```python
# 使用 HTML 创建格式化笔记
html_note = """
<h2>主要观点</h2>
<ul>
    <li>创新点1：提出了新的算法</li>
    <li>创新点2：改进了性能</li>
</ul>

<h2>个人评价</h2>
<p>这篇论文<strong>非常重要</strong>，值得<em>深入研究</em>。</p>

<h2>相关链接</h2>
<p><a href="https://example.com">相关资源</a></p>
```

note = client.add_item_note(
    item_key=item_key,
    note_text=html_note,
    title="深度阅读笔记"
)
```

### 从 Markdown 转换为 HTML

```python
# 可以使用 markdown 库转换
# pip install markdown

import markdown

md_text = """
## 主要内容

这篇论文讨论了：

1. 背景介绍
2. 方法论
3. 实验结果

**结论**：方法有效
"""

html = markdown.markdown(md_text)

note = client.add_item_note(
    item_key=item_key,
    note_text=html,
    title="Markdown 笔记"
)
```

## 实用示例

### 批量导出笔记

```python
def export_all_notes(client, output_file='notes_export.txt'):
    """导出所有笔记到文本文件"""
    # 获取所有条目
    items = client.get_items_top(limit=100)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in items:
            item_key = item['key']
            title = item.get('data', {}).get('title', '无标题')
            
            # 获取该条目的笔记
            notes = client.get_item_notes(item_key)
            
            if notes:
                f.write(f"\n{'='*60}\n")
                f.write(f"文献: {title}\n")
                f.write(f"{'='*60}\n\n")
                
                for i, note in enumerate(notes, 1):
                    content = note.get('data', {}).get('note', '')
                    # 简单去除 HTML 标签
                    plain = content.replace('<p>', '').replace('</p>', '\n')
                    plain = plain.replace('<strong>', '**').replace('</strong>', '**')
                    
                    f.write(f"笔记 {i}:\n{plain}\n\n")
    
    print(f"笔记已导出到 {output_file}")

# 使用
export_all_notes(client)
```

### 搜索笔记内容

```python
def search_notes(client, keyword):
    """在所有笔记中搜索关键词"""
    items = client.get_items_top(limit=100)
    matched_notes = []
    
    for item in items:
        item_key = item['key']
        item_title = item.get('data', {}).get('title', '无标题')
        
        notes = client.get_item_notes(item_key)
        
        for note in notes:
            content = note.get('data', {}).get('note', '').lower()
            if keyword.lower() in content:
                matched_notes.append({
                    'item_title': item_title,
                    'item_key': item_key,
                    'note': note
                })
    
    return matched_notes

# 搜索包含 "重要" 的笔记
results = search_notes(client, "重要")
print(f"找到 {len(results)} 条包含关键词的笔记")

for result in results:
    print(f"\n文献: {result['item_title']}")
    content = result['note'].get('data', {}).get('note', '')[:100]
    print(f"笔记片段: {content}...")
```

### 统计笔记数量

```python
def count_notes_per_item(client):
    """统计每篇文献的笔记数量"""
    items = client.get_items_top(limit=50)
    stats = []
    
    for item in items:
        item_key = item['key']
        title = item.get('data', {}).get('title', '无标题')
        notes = client.get_item_notes(item_key)
        
        if notes:  # 只统计有笔记的文献
            stats.append({
                'title': title,
                'note_count': len(notes)
            })
    
    # 按笔记数量排序
    stats.sort(key=lambda x: x['note_count'], reverse=True)
    
    print("笔记数量排行：")
    for i, item in enumerate(stats[:10], 1):
        print(f"{i}. {item['title']}: {item['note_count']} 条笔记")

# 使用
count_notes_per_item(client)
```

### 为一组文献添加相同笔记

```python
# 为搜索结果中的所有文献添加笔记
results = client.search_items("machine learning")

template_note = "待深入阅读：机器学习相关文献"

for item in results[:5]:  # 只处理前 5 篇
    item_key = item['key']
    title = item.get('data', {}).get('title', '无标题')
    
    try:
        client.add_item_note(
            item_key=item_key,
            note_text=template_note
        )
        print(f"✅ 已为 \"{title}\" 添加笔记")
    except Exception as e:
        print(f"❌ 添加失败: {e}")
```

## 笔记模板

### 阅读笔记模板

```python
def create_reading_note_template(rating, summary, highlights):
    """创建标准化的阅读笔记"""
    template = f"""
    <h2>📖 阅读笔记</h2>
    
    <h3>评分</h3>
    <p>{'⭐' * rating}/5</p>
    
    <h3>摘要</h3>
    <p>{summary}</p>
    
    <h3>重点内容</h3>
    <ul>
    """
    
    for highlight in highlights:
        template += f"    <li>{highlight}</li>\n"
    
    template += """
    </ul>
    
    <h3>阅读日期</h3>
    <p>{}</p>
    """.format(datetime.now().strftime('%Y-%m-%d'))
    
    return template

# 使用模板
from datetime import datetime

note_content = create_reading_note_template(
    rating=5,
    summary="这篇论文提出了一种新的深度学习方法...",
    highlights=[
        "创新点：注意力机制的新应用",
        "实验结果：在多个数据集上达到SOTA",
        "局限性：计算成本较高"
    ]
)

client.add_item_note(
    item_key=item_key,
    note_text=note_content,
    title="阅读笔记"
)
```

## 错误处理

```python
from zoteroapi import ZoteroLocalError

# 添加笔记时的错误处理
try:
    note = client.add_item_note(
        item_key="INVALID_KEY",
        note_text="测试笔记"
    )
except ZoteroLocalError as e:
    print(f"添加笔记失败: {e}")

# 获取笔记时的错误处理
try:
    note = client.get_note("INVALID_NOTE_KEY")
except ZoteroLocalError as e:
    print(f"获取笔记失败: {e}")
```

## 最佳实践

1. **使用有意义的标题**：

```python
# ✅ 好的做法
client.add_item_note(
    item_key=item_key,
    note_text=content,
    title="2024-01-15 第一次阅读"
)

# ❌ 不好的做法
client.add_item_note(
    item_key=item_key,
    note_text=content
)  # 没有标题
```

2. **结构化笔记内容**：使用 HTML 标题、列表等组织内容

3. **添加时间戳**：在笔记中包含创建日期

4. **检查父条目是否存在**：

```python
try:
    item = client.get_item(item_key)
    note = client.add_item_note(item_key, note_text)
except ResourceNotFound:
    print("父条目不存在")
```

## 下一步

- 📎 [文件操作](files.md)
- 🏷️ [标签管理](tags.md)
- 💡 [笔记操作示例](../examples/note-operations.md)

## 相关资源

- [API 参考 - NotesMixin](../api-reference/mixins/notes.md)
- [示例代码 - 笔记操作](../examples/note-operations.md)
