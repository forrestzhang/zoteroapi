# 笔记操作示例

本文档展示了如何使用 ZoteroAPI 进行笔记的创建、获取和管理操作。

## 获取笔记

### 获取单个笔记

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

try:
    # 通过笔记 key 获取笔记
    note = client.get_note("NOTE_KEY_HERE")

    # 提取笔记内容
    note_data = note.get('data', {})
    note_content = note_data.get('note', '')
    title = note_data.get('title', '无标题')

    print(f"笔记标题: {title}")
    print(f"笔记内容: {note_content}")

except Exception as e:
    print(f"获取笔记失败: {e}")
```

### 获取文献的所有笔记

```python
def get_all_item_notes(item_key):
    """获取某个文献的所有笔记"""

    try:
        notes = client.get_item_notes(item_key)

        print(f"文献 {item_key} 的笔记:")
        print("=" * 40)

        for i, note in enumerate(notes, 1):
            note_data = note.get('data', {})
            note_content = note_data.get('note', '')
            created = note_data.get('dateAdded', '')

            print(f"笔记 {i}:")
            print(f"创建时间: {created}")
            print(f"内容: {note_content[:200]}..." if len(note_content) > 200 else f"内容: {note_content}")
            print("-" * 40)

        return notes

    except Exception as e:
        print(f"获取笔记失败: {e}")
        return []

# 使用示例
# notes = get_all_item_notes("ITEM_KEY_HERE")
```

### 批量获取笔记

```python
def batch_get_notes(item_keys):
    """批量获取多个文献的笔记"""

    all_notes = {}

    for item_key in item_keys:
        try:
            # 获取文献信息
            item = client.get_item(item_key)
            item_title = item.get('data', {}).get('title', '未知文献')

            # 获取笔记
            notes = client.get_item_notes(item_key)

            if notes:
                all_notes[item_key] = {
                    'title': item_title,
                    'notes': notes,
                    'count': len(notes)
                }
                print(f"✓ {item_title}: {len(notes)} 条笔记")
            else:
                print(f"- {item_title}: 无笔记")

        except Exception as e:
            print(f"✗ 处理 {item_key} 失败: {e}")

    return all_notes

# 使用示例
# item_list = ["KEY1", "KEY2", "KEY3"]
# all_notes = batch_get_notes(item_list)
```

## 创建笔记

### 添加简单笔记

```python
def add_simple_note(item_key, note_text):
    """添加简单的文本笔记"""

    try:
        # 将纯文本转换为 HTML 格式（Zotero 笔记使用 HTML）
        html_note = f"<p>{note_text}</p>"

        # 添加笔记
        new_note = client.add_item_note(item_key, html_note)

        print(f"笔记添加成功!")
        print(f"笔记 key: {new_note['key']}")
        return new_note

    except Exception as e:
        print(f"添加笔记失败: {e}")
        return None

# 使用示例
# note = add_simple_note("ITEM_KEY_HERE", "这是一条测试笔记内容")
```

### 添加格式化笔记

```python
def add_formatted_note(item_key, title, content, tags=None):
    """添加带有格式的笔记"""

    # 构建 HTML 格式的笔记
    html_content = f"""
    <h2>{title}</h2>
    <div>
        {content}
    </div>
    <p><br></p>
    <p><em>创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    """

    try:
        # 添加笔记
        new_note = client.add_item_note(item_key, html_content, title=title)

        print(f"格式化笔记添加成功!")
        print(f"标题: {title}")
        print(f"笔记 key: {new_note['key']}")

        return new_note

    except Exception as e:
        print(f"添加格式化笔记失败: {e}")
        return None

# 使用示例
import time

title = "研究要点总结"
content = """
<h3>主要发现</h3>
<ul>
    <li>第一个重要发现</li>
    <li>第二个重要发现</li>
</ul>

<h3>待解决问题</h3>
<ol>
    <li>问题1</li>
    <li>问题2</li>
</ol>

<h3>后续研究方向</h3>
<p>基于本研究，后续可以从以下几个方向继续深入...</p>
"""

# note = add_formatted_note("ITEM_KEY_HERE", title, content)
```

### 添加阅读笔记模板

```python
def add_reading_note(item_key):
    """添加标准阅读笔记模板"""

    # 获取文献信息
    try:
        item = client.get_item(item_key)
        item_data = item.get('data', {})
        title = item_data.get('title', '未知标题')
        authors = item_data.get('creators', [])

        # 构建作者列表
        author_names = []
        for author in authors:
            if author.get('creatorType') == 'author':
                last_name = author.get('lastName', '')
                first_name = author.get('firstName', '')
                if last_name:
                    author_names.append(f"{last_name}, {first_name[0]}" if first_name else last_name)

        author_text = ', '.join(author_names[:3])
        if len(author_names) > 3:
            author_text += ' et al.'

    except:
        title = "未知文献"
        author_text = "未知作者"

    # 构建阅读笔记模板
    note_template = f"""
    <h1>阅读笔记</h1>

    <h2>文献信息</h2>
    <p><strong>标题:</strong> {title}</p>
    <p><strong>作者:</strong> {author_text}</p>
    <p><strong>阅读日期:</strong> {time.strftime('%Y-%m-%d')}</p>

    <h2>核心内容</h2>
    <h3>研究问题</h3>
    <p>• </p>
    <p>• </p>

    <h3>主要贡献</h3>
    <p>1. </p>
    <p>2. </p>
    <p>3. </p>

    <h3>方法论</h3>
    <p>• </p>
    <p>• </p>

    <h2>关键观点</h2>
    <p>• </p>
    <p>• </p>

    <h2>个人思考</h2>
    <h3>启发与收获</h3>
    <p>• </p>

    <h3>疑问与批判</h3>
    <p>• </p>

    <h3>应用价值</h3>
    <p>• </p>

    <h2>相关文献</h3>
    <p>• </p>
    <p>• </p>

    <h2>后续行动</h3>
    <p>• </p>
    <p>• </p>
    """

    try:
        new_note = client.add_item_note(item_key, note_template, f"阅读笔记: {title}")

        print(f"阅读笔记模板创建成功!")
        print(f"文献: {title}")
        print(f"笔记 key: {new_note['key']}")

        return new_note

    except Exception as e:
        print(f"创建阅读笔记失败: {e}")
        return None

# 使用示例
# reading_note = add_reading_note("ITEM_KEY_HERE")
```

## 笔记管理

### 笔记内容分析

```python
def analyze_note_content(notes):
    """分析笔记内容"""

    if not notes:
        print("没有笔记需要分析")
        return

    import re
    from bs4 import BeautifulSoup  # 需要安装: pip install beautifulsoup4

    total_notes = len(notes)
    total_length = 0
    word_counts = []

    print(f"分析 {total_notes} 条笔记:")
    print("=" * 50)

    for i, note in enumerate(notes, 1):
        note_data = note.get('data', {})
        note_content = note_data.get('note', '')
        created = note_data.get('dateAdded', '')

        # 使用 BeautifulSoup 清理 HTML 标签
        soup = BeautifulSoup(note_content, 'html.parser')
        clean_text = soup.get_text()

        # 统计信息
        char_count = len(clean_text)
        word_count = len(re.findall(r'\w+', clean_text))

        total_length += char_count
        word_counts.append(word_count)

        print(f"笔记 {i}:")
        print(f"  创建时间: {created}")
        print(f"  字符数: {char_count}")
        print(f"  词数: {word_count}")
        print(f"  内容预览: {clean_text[:100]}...")
        print()

    # 总结统计
    avg_length = total_length / total_notes
    avg_words = sum(word_counts) / total_notes

    print("统计总结:")
    print(f"  平均笔记长度: {avg_length:.1f} 字符")
    print(f"  平均词数: {avg_words:.1f} 词")
    print(f"  最长笔记: {max(word_counts)} 词")
    print(f"  最短笔记: {min(word_counts)} 词")

# 使用示例
# notes = client.get_item_notes("ITEM_KEY_HERE")
# analyze_note_content(notes)
```

### 笔记搜索

```python
def search_in_notes(item_key, search_term):
    """在笔记中搜索特定内容"""

    try:
        notes = client.get_item_notes(item_key)
        matching_notes = []

        for note in notes:
            note_data = note.get('data', {})
            note_content = note_data.get('note', '')

            # 简单的文本搜索（忽略 HTML 标签）
            if search_term.lower() in note_content.lower():
                matching_notes.append(note)

        print(f"在笔记中搜索 '{search_term}' 找到 {len(matching_notes)} 条匹配:")

        for i, note in enumerate(matching_notes, 1):
            note_data = note.get('data', {})
            note_content = note_data.get('note', '')

            # 高亮搜索词（简单实现）
            highlighted = note_content.replace(
                search_term,
                f"**{search_term}**"
            )

            print(f"\n匹配笔记 {i}:")
            print(f"笔记 key: {note.get('key')}")
            print(f"内容预览: {highlighted[:300]}...")

        return matching_notes

    except Exception as e:
        print(f"搜索笔记失败: {e}")
        return []

# 使用示例
# matches = search_in_notes("ITEM_KEY_HERE", "重要")
```

### 笔记导出

```python
def export_notes_to_markdown(item_keys, output_file="notes_export.md"):
    """将笔记导出为 Markdown 格式"""

    markdown_content = "# 文献笔记导出\n\n"

    for item_key in item_keys:
        try:
            # 获取文献信息
            item = client.get_item(item_key)
            item_data = item.get('data', {})
            title = item_data.get('title', '未知标题')
            authors = item_data.get('creators', [])

            # 构建作者列表
            author_names = []
            for author in authors:
                if author.get('creatorType') == 'author':
                    last_name = author.get('lastName', '')
                    first_name = author.get('firstName', '')
                    if last_name:
                        author_names.append(f"{last_name}, {first_name[0]}" if first_name else last_name)

            author_text = ', '.join(author_names[:3])
            if len(author_names) > 3:
                author_text += ' et al.'

            # 获取笔记
            notes = client.get_item_notes(item_key)

            if notes:
                markdown_content += f"## {title}\n\n"
                markdown_content += f"**作者:** {author_text}\n\n"

                for i, note in enumerate(notes, 1):
                    note_data = note.get('data', {})
                    note_content = note_data.get('note', '')
                    created = note_data.get('dateAdded', '')

                    # 简单的 HTML 到 Markdown 转换
                    import re
                    clean_content = re.sub(r'<[^>]+>', '', note_content)
                    clean_content = re.sub(r'\n\s*\n', '\n\n', clean_content)

                    markdown_content += f"### 笔记 {i}\n\n"
                    markdown_content += f"**创建时间:** {created}\n\n"
                    markdown_content += f"{clean_content}\n\n"
                    markdown_content += "---\n\n"

                markdown_content += "\n"

        except Exception as e:
            print(f"处理文献 {item_key} 失败: {e}")
            continue

    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"笔记已导出到: {output_file}")
        return output_file

    except Exception as e:
        print(f"导出失败: {e}")
        return None

# 使用示例
# item_list = ["KEY1", "KEY2", "KEY3"]
# export_notes_to_markdown(item_list, "my_notes.md")
```

## 高级笔记操作

### 批量创建摘要笔记

```python
def create_summary_note(collection_key):
    """为文献集创建摘要笔记"""

    try:
        # 获取文献集中的所有文献
        items = client.get_collection_items(collection_key)

        if not items:
            print("文献集中没有文献")
            return None

        # 构建摘要内容
        summary_content = "<h1>文献集摘要</h1>\n\n"

        for i, item in enumerate(items, 1):
            item_data = item.get('data', {})
            title = item_data.get('title', '未知标题')
            abstract = item_data.get('abstractNote', '')
            publication = item_data.get('publicationTitle', '')
            year = item_data.get('date', '')

            # 构建文献条目摘要
            summary_content += f"<h2>{i}. {title}</h2>\n"

            if publication:
                summary_content += f"<p><strong>期刊:</strong> {publication}"
                if year:
                    summary_content += f" ({year})"
                summary_content += "</p>\n"

            if abstract:
                # 限制摘要长度
                if len(abstract) > 500:
                    abstract = abstract[:500] + "..."
                summary_content += f"<p><strong>摘要:</strong> {abstract}</p>\n"

            # 获取笔记数量
            try:
                notes = client.get_item_notes(item['key'])
                if notes:
                    summary_content += f"<p><strong>笔记:</strong> {len(notes)} 条</p>\n"
            except:
                pass

            summary_content += "<hr>\n\n"

        # 添加创建时间
        summary_content += f"<p><em>摘要生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</em></p>"

        # 创建摘要笔记（创建在第一个文献下）
        first_item_key = items[0]['key']
        summary_note = client.add_item_note(
            first_item_key,
            summary_content,
            "文献集摘要"
        )

        print(f"摘要笔记创建成功!")
        print(f"包含 {len(items)} 篇文献")
        print(f"笔记 key: {summary_note['key']}")

        return summary_note

    except Exception as e:
        print(f"创建摘要笔记失败: {e}")
        return None

# 使用示例
# summary = create_summary_note("COLLECTION_KEY_HERE")
```

### 笔记统计分析

```python
def analyze_all_notes(collection_key=None):
    """统计分析所有笔记"""

    import re
    from collections import Counter
    from bs4 import BeautifulSoup

    try:
        # 获取文献列表
        if collection_key:
            items = client.get_collection_items(collection_key)
            print(f"分析文献集中的笔记...")
        else:
            items = client.get_items_top(limit=100)
            print(f"分析顶层文献的笔记...")

        total_notes = 0
        total_words = 0
        notes_per_item = []
        note_lengths = []
        all_words = []

        for item in items:
            try:
                notes = client.get_item_notes(item['key'])
                item_note_count = len(notes)
                notes_per_item.append(item_note_count)

                for note in notes:
                    note_data = note.get('data', {})
                    note_content = note_data.get('note', '')

                    # 清理 HTML 并统计
                    soup = BeautifulSoup(note_content, 'html.parser')
                    clean_text = soup.get_text()

                    words = re.findall(r'\w+', clean_text.lower())
                    all_words.extend(words)

                    note_lengths.append(len(clean_text))
                    total_words += len(words)
                    total_notes += 1

            except:
                continue

        if total_notes == 0:
            print("没有找到笔记")
            return

        # 统计分析
        word_freq = Counter(all_words)

        print("=" * 60)
        print("笔记统计分析")
        print("=" * 60)
        print(f"总文献数: {len(items)}")
        print(f"有笔记的文献: {len([x for x in notes_per_item if x > 0])}")
        print(f"总笔记数: {total_notes}")
        print(f"总词数: {total_words}")
        print(f"平均每篇文献笔记数: {total_notes/len(items):.2f}")
        print(f"平均每条笔记词数: {total_words/total_notes:.2f}")
        print()

        print("高频词汇 (前20个):")
        for word, count in word_freq.most_common(20):
            if len(word) > 2:  # 过滤短词
                print(f"  {word}: {count} 次")

        return {
            'total_items': len(items),
            'total_notes': total_notes,
            'total_words': total_words,
            'word_frequency': word_freq
        }

    except Exception as e:
        print(f"分析失败: {e}")
        return None

# 使用示例
# stats = analyze_all_notes()
```

## 小结

- 使用 `get_note()` 获取单个笔记
- 使用 `get_item_notes()` 获取文献的所有笔记
- 使用 `add_item_note()` 创建新笔记
- 笔记内容使用 HTML 格式
- 实现笔记搜索、导出和分析功能
- 创建标准化的笔记模板

这些功能可以帮助你有效地管理研究笔记和知识积累。