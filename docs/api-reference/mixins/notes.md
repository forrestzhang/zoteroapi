# NotesMixin

`NotesMixin` 提供了笔记管理相关功能的 Mixin 类，包括笔记的创建、获取、搜索和管理操作。

## 类定义

```python
class NotesMixin:
    """笔记管理 Mixin 类"""
```

## 主要方法

### get_note()

```python
def get_note(self, note_key: str) -> Dict:
    """
    通过笔记 key 获取笔记

    Args:
        note_key: 笔记的唯一标识符

    Returns:
        Dict: 包含完整笔记信息的字典

    Raises:
        ZoteroLocalError: 当笔记获取失败或不存在时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> note = client.get_note("NOTE_KEY_HERE")
        >>> content = note['data']['note']
        >>> print(f"笔记内容: {content}")

    Note:
        会验证返回的确实是笔记类型（itemType: 'note'）
        笔记内容通常为 HTML 格式
    """
```

### get_item_notes()

```python
def get_item_notes(self, item_key: str) -> List[Dict]:
    """
    获取某个文献的所有笔记

    Args:
        item_key: 文献的唯一标识符

    Returns:
        List[Dict]: 笔记列表，每个元素为笔记对象

    Raises:
        ZoteroLocalError: 当笔记获取失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> notes = client.get_item_notes("ITEM_KEY_HERE")
        >>> print(f"共有 {len(notes)} 条笔记")
        >>> for i, note in enumerate(notes, 1):
        ...     content = note['data']['note']
        ...     print(f"笔记 {i}: {content[:100]}...")

    Note:
        返回的笔记按创建时间排序
        只返回笔记类型的子条目
    """
```

### add_item_note()

```python
def add_item_note(self, item_key: str, note_text: str, title: Optional[str] = None) -> Dict:
    """
    为文献添加笔记

    Args:
        item_key: 文献的唯一标识符
        note_text: 笔记内容（HTML 格式）
        title: 笔记标题（可选）

    Returns:
        Dict: 创建的笔记对象

    Raises:
        ZoteroLocalError: 当笔记创建失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> # 添加简单笔记
        >>> note = client.add_item_note(
        ...     "ITEM_KEY_HERE",
        ...     "<p>这是一条简单的笔记内容</p>"
        ... )

        >>> # 添加带标题的格式化笔记
        >>> html_content = """
        ... <h2>研究要点</h2>
        ... <ul>
        ...     <li>第一个要点</li>
        ...     <li>第二个要点</li>
        ... </ul>
        ... """
        >>> note = client.add_item_note(
        ...     "ITEM_KEY_HERE",
        ...     html_content,
        ...     title="研究要点"
        ... )

    Note:
        - 笔记内容必须使用 HTML 格式
        - 会自动创建笔记条目并关联到父文献
        - 返回的是完整的笔记对象，包含生成的 key
    """
```

## 笔记数据结构

### 笔记对象格式

```python
{
    "key": "NOTE123XYZ",
    "version": 123,
    "library": {
        "type": "user",
        "id": 12345
    },
    "links": {
        "self": {...},
        "up": {...}
    },
    "meta": {
        "createdByUser": {...},
        "numChildren": 0
    },
    "data": {
        "key": "NOTE123XYZ",
        "version": 123,
        "itemType": "note",
        "parentItem": "PARENT_ITEM_KEY",
        "note": "<p>笔记内容</p>",
        "tags": [],
        "collections": [],
        "relations": {},
        "dateAdded": "2024-01-01T12:00:00Z",
        "dateModified": "2024-01-01T12:00:00Z"
    }
}
```

### 常用字段说明

- `key`: 笔记的唯一标识符
- `itemType`: 固定为 "note"
- `parentItem`: 父文献的 key
- `note`: 笔记的 HTML 内容
- `dateAdded`: 创建时间
- `dateModified`: 修改时间

## 实现细节

### 笔记创建流程

`add_item_note` 方法的实现分为两步：

1. **创建笔记条目**：
   ```python
   note_template = {
       "itemType": "note",
       "parentItem": item_key,
       "note": note_text,
       "tags": [],
       "collections": [],
       "relations": {}
   }

   if title:
       note_template["title"] = title

   create_response = self._make_request(
       "POST",
       "/items",
       data={"items": [note_template]}
   )
   ```

2. **返回创建的笔记**：
   ```python
   result = create_response.json()
   if "success" in result:
       success = result.get("success", {})
       if success:
           new_note_key = next(iter(success.values()))
           return self.get_note(new_note_key)
   ```

### 笔记获取和过滤

```python
def get_item_notes(self, item_key: str) -> List[Dict]:
    # 获取所有子条目
    response = self._make_request("GET", f"/items/{item_key}/children")
    items = response.json()

    # 只返回笔记类型的条目
    notes = [
        item for item in items
        if item.get('data', {}).get('itemType') == 'note'
    ]

    return notes
```

## 扩展功能

### 高级笔记操作

```python
class AdvancedNotesMixin(NotesMixin):
    """高级笔记操作 Mixin"""

    def search_in_notes(self, item_key: str, search_term: str) -> List[Dict]:
        """在文献的所有笔记中搜索"""
        notes = self.get_item_notes(item_key)
        matching_notes = []

        for note in notes:
            note_content = note.get('data', {}).get('note', '')
            # 简单的文本搜索（忽略 HTML 标签）
            if search_term.lower() in note_content.lower():
                matching_notes.append(note)

        return matching_notes

    def export_notes_to_text(self, item_key: str) -> str:
        """将笔记导出为纯文本"""
        from bs4 import BeautifulSoup

        notes = self.get_item_notes(item_key)
        text_content = []

        for i, note in enumerate(notes, 1):
            note_data = note.get('data', {})
            note_content = note_data.get('note', '')
            created = note_data.get('dateAdded', '')

            # 清理 HTML 标签
            soup = BeautifulSoup(note_content, 'html.parser')
            clean_text = soup.get_text()

            text_content.append(f"笔记 {i}:")
            text_content.append(f"创建时间: {created}")
            text_content.append(f"内容: {clean_text}")
            text_content.append("-" * 40)

        return "\n".join(text_content)

    def get_note_statistics(self, item_key: str) -> Dict:
        """获取笔记统计信息"""
        notes = self.get_item_notes(item_key)

        if not notes:
            return {
                'total_notes': 0,
                'total_characters': 0,
                'total_words': 0,
                'average_length': 0
            }

        total_chars = 0
        total_words = 0

        for note in notes:
            note_content = note.get('data', {}).get('note', '')
            # 清理 HTML 标签
            soup = BeautifulSoup(note_content, 'html.parser')
            clean_text = soup.get_text()

            total_chars += len(clean_text)
            total_words += len(clean_text.split())

        return {
            'total_notes': len(notes),
            'total_characters': total_chars,
            'total_words': total_words,
            'average_length': total_chars / len(notes)
        }

    def update_note(self, note_key: str, new_content: str) -> Dict:
        """更新现有笔记内容"""
        try:
            # 获取现有笔记
            note = self.get_note(note_key)
            note_data = note.get('data', {})

            # 更新内容
            note_data['note'] = new_content

            # 发送更新请求
            response = self._make_request(
                "PUT",
                f"/items/{note_key}",
                data=note_data
            )

            return response.json()

        except Exception as e:
            raise ZoteroLocalError(f"Failed to update note: {str(e)}")

    def delete_note(self, note_key: str) -> bool:
        """删除笔记"""
        try:
            self._make_request("DELETE", f"/items/{note_key}")
            return True
        except Exception as e:
            raise ZoteroLocalError(f"Failed to delete note: {str(e)}")
```

### 笔记模板生成

```python
class NoteTemplateMixin(NotesMixin):
    """笔记模板 Mixin"""

    def create_reading_template(self) -> str:
        """创建阅读笔记模板"""
        import time

        return f"""
        <h1>阅读笔记</h1>
        <h2>基本信息</h2>
        <p><strong>阅读日期:</strong> {time.strftime('%Y-%m-%d')}</p>

        <h2>核心内容</h2>
        <h3>研究问题</h3>
        <ul>
            <li>• </li>
            <li>• </li>
        </ul>

        <h3>主要发现</h3>
        <ol>
            <li></li>
            <li></li>
        </ol>

        <h2>个人思考</h2>
        <h3>启发与收获</h3>
        <p>• </p>

        <h3>疑问与批判</h3>
        <p>• </p>

        <h2>后续行动</h2>
        <p>• </p>
        """

    def create_meeting_template(self) -> str:
        """创建会议记录模板"""
        import time

        return f"""
        <h1>会议记录</h1>
        <h2>会议信息</h2>
        <p><strong>日期:</strong> {time.strftime('%Y-%m-%d')}</p>
        <p><strong>时间:</strong> </p>
        <p><strong>地点:</strong> </p>
        <p><strong>参会人员:</strong> </p>

        <h2>议程</h2>
        <ol>
            <li></li>
            <li></li>
        </ol>

        <h2>讨论要点</h2>
        <ul>
            <li><strong>要点1:</strong> </li>
            <li><strong>要点2:</strong> </li>
        </ul>

        <h2>决议事项</h2>
        <ul>
            <li>• </li>
            <li>• </li>
        </ul>

        <h2>行动项</h2>
        <table border="1">
            <tr><th>事项</th><th>负责人</th><th>截止日期</th></tr>
            <tr><td></td><td></td><td></td></tr>
        </table>
        """

    def add_template_note(self, item_key: str, template_type: str = "reading") -> Dict:
        """添加模板笔记"""
        if template_type == "reading":
            content = self.create_reading_template()
            title = "阅读笔记模板"
        elif template_type == "meeting":
            content = self.create_meeting_template()
            title = "会议记录模板"
        else:
            raise ValueError(f"Unknown template type: {template_type}")

        return self.add_item_note(item_key, content, title)
```

### 笔记导出功能

```python
class NoteExportMixin(NotesMixin):
    """笔记导出 Mixin"""

    def export_notes_to_markdown(self, item_key: str) -> str:
        """导出为 Markdown 格式"""
        notes = self.get_item_notes(item_key)
        markdown_content = []

        for i, note in enumerate(notes, 1):
            note_data = note.get('data', {})
            note_content = note_data.get('note', '')
            created = note_data.get('dateAdded', '')

            # 简单的 HTML 到 Markdown 转换
            clean_content = self._html_to_markdown(note_content)

            markdown_content.append(f"## 笔记 {i}")
            markdown_content.append(f"**创建时间:** {created}")
            markdown_content.append("")
            markdown_content.append(clean_content)
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")

        return "\n".join(markdown_content)

    def _html_to_markdown(self, html_content: str) -> str:
        """简单的 HTML 到 Markdown 转换"""
        import re

        # 基本的 HTML 标签转换
        content = html_content

        # 标题
        content = re.sub(r'<h([1-6])>(.*?)</h\1>', r'\n## \2\n', content)

        # 段落
        content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content)

        # 列表
        content = re.sub(r'<li>(.*?)</li>', r'- \1\n', content)
        content = re.sub(r'<ul>|</ul>', '', content)
        content = re.sub(r'<ol>|</ol>', '', content)

        # 粗体
        content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)

        # 斜体
        content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)

        # 链接
        content = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', content)

        # 清理剩余的 HTML 标签
        content = re.sub(r'<[^>]+>', '', content)

        # 清理多余的空白
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content.strip()

    def save_notes_to_file(self, item_key: str, filename: str, format: str = "markdown") -> str:
        """保存笔记到文件"""
        if format == "markdown":
            content = self.export_notes_to_markdown(item_key)
        elif format == "text":
            content = self.export_notes_to_text(item_key)
        else:
            raise ValueError(f"Unsupported format: {format}")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            return filename

        except Exception as e:
            raise ZoteroLocalError(f"Failed to save notes: {str(e)}")
```

## 使用示例

### 基础笔记操作

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# 获取文献的所有笔记
notes = client.get_item_notes("ITEM_KEY_HERE")
print(f"共有 {len(notes)} 条笔记")

for note in notes:
    content = note['data']['note']
    print(f"- {content[:50]}...")

# 添加新笔记
html_content = """
<h2>研究要点</h2>
<ul>
    <li>这是一个重要的发现</li>
    <li>需要进一步验证的结果</li>
</ul>
<p><em>创建时间: 2024-01-01</em></p>
"""

new_note = client.add_item_note(
    "ITEM_KEY_HERE",
    html_content,
    title="研究要点"
)

print(f"笔记已添加，key: {new_note['key']}")
```

### 高级功能使用

```python
class ExtendedZoteroClient(ZoteroLocal, AdvancedNotesMixin, NoteTemplateMixin):
    """扩展的 Zotero 客户端"""
    pass

client = ExtendedZoteroClient()

# 在笔记中搜索
matches = client.search_in_notes("ITEM_KEY_HERE", "重要")
print(f"找到 {len(matches)} 条匹配的笔记")

# 获取笔记统计
stats = client.get_note_statistics("ITEM_KEY_HERE")
print(f"笔记统计: {stats}")

# 添加模板笔记
template_note = client.add_template_note("ITEM_KEY_HERE", "reading")
print(f"模板笔记已添加: {template_note['key']}")

# 导出笔记
filename = client.save_notes_to_file("ITEM_KEY_HERE", "notes.md", "markdown")
print(f"笔记已导出到: {filename}")
```

## 注意事项

1. **HTML 格式**: 笔记内容必须使用 HTML 格式，纯文本会被当作 HTML 处理
2. **内容安全**: 避免在笔记中包含不安全的 HTML 内容
3. **性能限制**: 大量笔记操作时注意性能影响
4. **同步问题**: 笔记的创建和修改可能需要时间同步到 Zotero
5. **字符编码**: 确保使用 UTF-8 编码处理非 ASCII 字符
6. **长度限制**: 过长的笔记可能会影响性能和同步

`NotesMixin` 提供了完整的笔记管理功能，支持各种笔记创建、查询和导出操作。