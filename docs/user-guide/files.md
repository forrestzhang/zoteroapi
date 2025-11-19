# 文件操作

本页面介绍如何使用 ZoteroAPI 管理文献附件和文件。

## 下载文件

### 下载附件到指定路径

```python
from zoteroapi import ZoteroLocal
from pathlib import Path

client = ZoteroLocal()

# 获取一个带附件的条目（假设）
item_key = "ABC123"

# 下载文件到指定路径
save_path = Path.home() / "Downloads" / "paper.pdf"
client.download_file(item_key, save_path)

print(f"✅ 文件已下载到: {save_path}")
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| item_key | str | 附件条目的 key |
| path | str/Path | 保存文件的路径 |

### 获取文件内容

```python
# 获取文件的二进制内容
file_content = client.get_item_file(item_key)

# 保存到文件
with open("output.pdf", "wb") as f:
    f.write(file_content.read())
```

**返回值**：文件的二进制流 (BinaryIO)

## 上传文件

### 上传文件作为附件

```python
from pathlib import Path

# 上传文件并关联到文献
file_path = Path("~/Documents/paper.pdf").expanduser()

result = client.upload_file(
    file_path=file_path,
    parent_item="ABC123",  # 父文献的 key
    title="论文原文"  # 可选的标题
)

print(f"✅ 文件已上传，Key: {result['key']}")
```

**参数说明**：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| file_path | str/Path | 是 | 要上传的文件路径 |
| parent_item | str | 否 | 父文献的 key |
| title | str | 否 | 附件标题（默认使用文件名） |

**返回值**：上传后的附件对象

## 复制附件到下载目录

### 复制本地附件

```python
# 假设文献有一个本地附件
# file_uri 格式如：file:///Users/username/Zotero/storage/ABC123/paper.pdf

file_uri = "file:///Users/username/Zotero/storage/ABC123/paper.pdf"

# 复制到默认下载目录
dest_path = client.copy_attachment_to_downloads(file_uri)
print(f"✅ 文件已复制到: {dest_path}")

# 或复制到指定目录
custom_dir = Path.home() / "Documents" / "Papers"
dest_path = client.copy_attachment_to_downloads(file_uri, str(custom_dir))
```

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| file_uri | str | - | 文件 URI（通常从条目数据中获取） |
| download_dir | str | None | 目标目录（默认为 ~/Downloads） |

**返回值**：复制后的文件路径

!!! note "文件 URI"
    文件 URI 通常存储在附件条目的 `data.path` 字段中。

## 获取文献附件信息

### 获取附件列表

```python
# 获取文献的所有子项（包括附件）
item_key = "ABC123"
children = client._make_request("GET", f"/items/{item_key}/children").json()

# 筛选出附件
attachments = [
    child for child in children
    if child.get('data', {}).get('itemType') == 'attachment'
]

for att in attachments:
    data = att.get('data', {})
    title = data.get('title', '未命名')
    content_type = data.get('contentType', 'unknown')
    filename = data.get('filename', '')
    
    print(f"📎 {title} ({content_type})")
    if filename:
        print(f"   文件名: {filename}")
```

### 获取附件 URL

```python
items = client.get_items_top(limit=10)

for item in items:
    item_key = item['key']
    
    # 获取附件链接
    att_href = client.get_item_attachment_href(item_key)
    
    if att_href:
        print(f"文献: {item.get('data', {}).get('title', '无标题')}")
        print(f"附件链接: {att_href}\n")
```

## 实用示例

### 批量下载文献集的所有 PDF

```python
from pathlib import Path

def download_collection_pdfs(client, collection_key, output_dir):
    """下载文献集中所有文献的 PDF 附件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取文献集中的所有条目
    items = client.get_collection_items(collection_key)
    
    downloaded = 0
    for item in items:
        item_key = item['key']
        title = item.get('data', {}).get('title', '未命名')
        
        # 获取子项（包括附件）
        try:
            children = client._make_request(
                "GET", 
                f"/items/{item_key}/children"
            ).json()
            
            # 查找 PDF 附件
            for child in children:
                data = child.get('data', {})
                if (data.get('itemType') == 'attachment' and 
                    data.get('contentType') == 'application/pdf'):
                    
                    # 下载
                    pdf_key = child['key']
                    filename = data.get('filename', f"{item_key}.pdf")
                    save_path = output_dir / filename
                    
                    client.download_file(pdf_key, save_path)
                    print(f"✅ 已下载: {title}")
                    downloaded += 1
                    break
        except Exception as e:
            print(f"❌ 下载失败 ({title}): {e}")
    
    print(f"\n完成！共下载 {downloaded} 个 PDF 文件到 {output_dir}")

# 使用
download_collection_pdfs(
    client,
    collection_key="COLL123",
    output_dir="~/Documents/Papers"
)
```

### 复制带关键词的文献的 PDF

```python
def copy_pdfs_by_keyword(client, keyword, output_dir):
    """复制包含关键词的文献的 PDF 到指定目录"""
    # 搜索文献
    results = client.search_items(keyword)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    for item in results:
        item_key = item['key']
        title = item.get('data', {}).get('title', '未命名')
        
        # 获取附件 URI
        try:
            children = client._make_request(
                "GET",
                f"/items/{item_key}/children"
            ).json()
            
            for child in children:
                data = child.get('data', {})
                if data.get('itemType') == 'attachment':
                    file_path = data.get('path', '')
                    if file_path:
                        # 复制文件
                        dest = client.copy_attachment_to_downloads(
                            file_path,
                            str(output_dir)
                        )
                        print(f"✅ 已复制: {title}")
                        copied += 1
                        break
        except Exception as e:
            print(f"❌ 复制失败 ({title}): {e}")
    
    print(f"\n完成！共复制 {copied} 个文件")

# 使用
copy_pdfs_by_keyword(client, "machine learning", "~/Downloads/ML_Papers")
```

### 检查缺失附件

```python
def find_items_without_attachments(client, limit=100):
    """查找没有附件的文献"""
    items = client.get_items_top(limit=limit)
    no_attachment = []
    
    for item in items:
        if item.get('data', {}).get('itemType') == 'note':
            continue  # 跳过笔记
        
        item_key = item['key']
        
        try:
            children = client._make_request(
                "GET",
                f"/items/{item_key}/children"
            ).json()
            
            # 检查是否有附件
            has_attachment = any(
                child.get('data', {}).get('itemType') == 'attachment'
                for child in children
            )
            
            if not has_attachment:
                no_attachment.append(item)
        except:
            pass
    
    return no_attachment

# 查找缺失附件的文献
items = find_items_without_attachments(client)
print(f"找到 {len(items)} 篇没有附件的文献：\n")

for item in items[:10]:  # 显示前 10 篇
    title = item.get('data', {}).get('title', '无标题')
    print(f"  - {title}")
```

### 统计文件类型

```python
from collections import Counter

def count_attachment_types(client, limit=100):
    """统计附件文件类型"""
    items = client.get_items_top(limit=limit)
    types = []
    
    for item in items:
        item_key = item['key']
        
        try:
            children = client._make_request(
                "GET",
                f"/items/{item_key}/children"
            ).json()
            
            for child in children:
                data = child.get('data', {})
                if data.get('itemType') == 'attachment':
                    content_type = data.get('contentType', 'unknown')
                    types.append(content_type)
        except:
            pass
    
    # 统计
    type_counts = Counter(types)
    
    print("附件类型统计：")
    for file_type, count in type_counts.most_common():
        print(f"  {file_type}: {count}")

# 使用
count_attachment_types(client)
```

## 文件路径处理

### 跨平台路径处理

ZoteroAPI 自动处理不同操作系统的文件路径：

```python
# Windows 路径
file_uri_win = "file:///C:/Users/username/Zotero/storage/ABC123/paper.pdf"

# macOS/Linux 路径
file_uri_unix = "file:///Users/username/Zotero/storage/ABC123/paper.pdf"

# 自动识别并处理
dest = client.copy_attachment_to_downloads(file_uri_win)  # Windows
dest = client.copy_attachment_to_downloads(file_uri_unix)  # macOS/Linux
```

### URL 解码

文件路径中的特殊字符会被自动解码：

```python
# 包含中文或空格的文件名
file_uri = "file:///Users/username/Zotero/storage/ABC123/%E8%AE%BA%E6%96%87.pdf"

# 自动解码为: 论文.pdf
dest = client.copy_attachment_to_downloads(file_uri)
```

## 压缩文件处理

Zotero 有时会返回压缩的文件，ZoteroAPI 会自动解压：

```python
# 自动处理压缩文件
file_content = client.get_item_file(item_key)

# 如果文件被压缩，会自动解压并返回原始内容
with open("paper.pdf", "wb") as f:
    f.write(file_content.read())
```

## 错误处理

```python
from zoteroapi import ZoteroLocalError

# 下载文件
try:
    client.download_file("INVALID_KEY", "output.pdf")
except ZoteroLocalError as e:
    print(f"下载失败: {e}")

# 上传文件
try:
    client.upload_file("nonexistent.pdf")
except FileNotFoundError:
    print("文件不存在")
except ZoteroLocalError as e:
    print(f"上传失败: {e}")

# 复制附件
try:
    client.copy_attachment_to_downloads("invalid_uri")
except ZoteroLocalError as e:
    print(f"复制失败: {e}")
```

## 最佳实践

1. **检查文件是否存在**：

```python
from pathlib import Path

file_path = Path("paper.pdf")
if file_path.exists():
    client.upload_file(file_path)
else:
    print("文件不存在")
```

2. **创建目标目录**：

```python
output_dir = Path("~/Documents/Papers").expanduser()
output_dir.mkdir(parents=True, exist_ok=True)
```

3. **使用有意义的文件名**：

```python
# 使用文献标题作为文件名
title = item.get('data', {}).get('title', '未命名')
# 清理文件名中的非法字符
safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
filename = f"{safe_title}.pdf"
```

4. **批量操作时添加进度提示**：

```python
from tqdm import tqdm  # pip install tqdm

items = client.get_collection_items(collection_key)
for item in tqdm(items, desc="下载进度"):
    # 下载操作
    pass
```

## 下一步

- 📚 [文献条目管理](items-management.md)
- 🏷️ [标签管理](tags.md)
- 💡 [文件操作示例](../examples/file-operations.md)

## 相关资源

- [API 参考 - FilesMixin](../api-reference/mixins/files.md)
- [示例代码 - 文件操作](../examples/file-operations.md)
