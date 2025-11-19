# FilesMixin

`FilesMixin` 提供了文件相关操作的 Mixin 类，包括附件文件下载、复制和管理功能。支持处理压缩文件和跨平台的路径操作。

## 类定义

```python
class FilesMixin:
    """文件操作 Mixin 类"""
```

## 主要方法

### get_item_file()

```python
def get_item_file(self, item_key: str) -> BinaryIO:
    """
    获取条目的附件文件内容

    通过条目 key 下载附件文件的二进制内容。支持处理
    Zotero 自动压缩的文件。

    Args:
        item_key: 条目的唯一标识符

    Returns:
        BinaryIO: 文件内容的二进制流对象

    Raises:
        ZoteroLocalError: 当文件下载失败或条目不存在时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> file_content = client.get_item_file("ABC123")
        >>> with open("paper.pdf", "wb") as f:
        ...     f.write(file_content.read())

    Note:
        如果文件被压缩，会自动解压并返回第一个文件的内容
        返回的是二进制流对象，需要正确处理编码
    """
```

### copy_attachment_to_downloads()

```python
def copy_attachment_to_downloads(self, file_uri: str, download_dir: str = None) -> str:
    """
    复制附件文件到下载目录

    将 Zotero 附件文件复制到指定的下载目录。支持跨平台
    路径处理和自动目录创建。

    Args:
        file_uri: 文件的 URI 路径，如 'file:///path/to/file.pdf'
        download_dir: 目标下载目录。如果为 None，则使用系统默认下载目录

    Returns:
        str: 复制后文件的完整路径

    Raises:
        ZoteroLocalError: 当文件复制失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> # 复制到默认下载目录
        >>> dest_path = client.copy_attachment_to_downloads(
        ...     "file:///Users/name/Zotero/storage/ABC123/paper.pdf"
        ... )
        >>> print(f"文件已复制到: {dest_path}")

        >>> # 复制到指定目录
        >>> dest_path = client.copy_attachment_to_downloads(
        ...     "file:///Users/name/Zotero/storage/ABC123/paper.pdf",
        ...     "/path/to/custom/dir"
        ... )

    Note:
        - Windows 路径和 Unix 路径会自动处理
        - 目标目录不存在时会自动创建
        - 文件名保持不变
    """
```

### download_file()

```python
def download_file(self, item_key: str, path: Union[str, Path]) -> None:
    """
    下载条目的附件文件到指定路径

    Args:
        item_key: 条目ID
        path: 保存路径

    Raises:
        ZoteroLocalError: 当下载失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> client.download_file("ABC123", "./downloads/paper.pdf")
    """
```

### upload_file()

```python
def upload_file(self,
               file_path: Union[str, Path],
               parent_item: Optional[str] = None,
               title: Optional[str] = None) -> Dict:
    """
    上传文件作为附件

    Args:
        file_path: 文件路径
        parent_item: 父条目ID（可选）
        title: 附件标题（可选，默认使用文件名）

    Returns:
        Dict: 上传结果

    Raises:
        ZoteroLocalError: 当上传失败时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> result = client.upload_file(
        ...     "/path/to/paper.pdf",
        ...     parent_item="PARENT_KEY",
        ...     title="研究论文"
        ... )
    """
```

### get_item_attachment_href()

```python
def get_item_attachment_href(self, item_key: str) -> str:
    """
    获取条目附件的直接下载链接

    Args:
        item_key: 条目ID

    Returns:
        str: 附件的直接下载链接

    Raises:
        ZoteroLocalError: 当无法获取附件链接或附件不是PDF时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> href = client.get_item_attachment_href("ABC123")
        >>> print(f"下载链接: {href}")
    """
```

## 私有方法

### _normalize_path()

```python
def _normalize_path(self, file_uri: str) -> str:
    """
    将文件 URI 标准化为系统路径

    处理不同操作系统的文件 URI 格式，转换为有效的本地路径。

    Args:
        file_uri: 文件 URI，如 'file:///path/to/file.pdf' 或 'file://C:/path/to/file.pdf'

    Returns:
        str: 标准化的本地文件路径

    Note:
        - Windows 系统会去掉开头的 'file:///'
        - Unix 系统会去掉开头的 'file://'
        - 自动处理 URL 编码字符
    """
```

### _guess_mimetype()

```python
def _guess_mimetype(self, file_path: Path) -> str:
    """
    猜测文件的 MIME 类型

    Args:
        file_path: 文件路径

    Returns:
        str: MIME 类型字符串，默认为 'application/octet-stream'
    """
```

### _calculate_md5()

```python
def _calculate_md5(self, file_path: Path) -> str:
    """
    计算文件的 MD5 值

    Args:
        file_path: 文件路径

    Returns:
        str: 文件的 MD5 哈希值（十六进制字符串）
    """
```

## 实现细节

### 文件压缩处理

Zotero 有时会压缩附件文件以提高传输效率。`FilesMixin` 自动处理压缩文件：

```python
def get_item_file(self, item_key: str) -> BinaryIO:
    response = self._make_request("GET", f"/items/{item_key}/file")

    # 检查是否是压缩文件
    if (response.headers.get('Content-Type') == 'application/zip' and
        response.headers.get('Zotero-File-Compressed') == 'Yes'):
        z = zipfile.ZipFile(io.BytesIO(response.content))
        return io.BytesIO(z.read(z.namelist()[0]))  # 返回第一个文件

    return io.BytesIO(response.content)
```

### 跨平台路径处理

自动处理不同操作系统的文件路径差异：

```python
def _normalize_path(self, file_uri: str) -> str:
    if platform.system() == 'Windows':
        # Windows: file:///C:/path/to/file.pdf -> C:/path/to/file.pdf
        path = file_uri.replace('file:///', '')
    else:
        # Unix: file:///path/to/file.pdf -> /path/to/file.pdf
        path = file_uri.replace('file://', '')

    path = unquote(path)  # 处理 URL 编码
    return str(Path(path))
```

### 文件上传流程

文件上传分为两步：

1. **创建附件条目**：
   ```python
   file_data = {
       "filename": file_path.name,
       "title": title or file_path.name,
       "contentType": self._guess_mimetype(file_path),
       "md5": self._calculate_md5(file_path)
   }

   if parent_item:
       file_data["parentItem"] = parent_item

   response = self._make_request("POST", "/items", data={"items": [file_data]})
   item_key = response.json()["successful"][0]["key"]
   ```

2. **上传文件内容**：
   ```python
   with open(file_path, 'rb') as f:
       self._make_request("POST", f"/items/{item_key}/file", files={"file": f})
   ```

## 扩展功能

### 批量文件操作

```python
class BatchFilesMixin(FilesMixin):
    """批量文件操作 Mixin"""

    def download_all_attachments(self, item_keys: List[str], output_dir: str) -> List[str]:
        """批量下载附件"""
        downloaded_files = []

        for item_key in item_keys:
            try:
                file_content = self.get_item_file(item_key)
                # 需要获取文件名（这里需要额外实现）
                filename = f"attachment_{item_key}.pdf"
                file_path = os.path.join(output_dir, filename)

                with open(file_path, 'wb') as f:
                    f.write(file_content.read())

                downloaded_files.append(file_path)
            except Exception as e:
                print(f"下载 {item_key} 失败: {e}")

        return downloaded_files

    def get_attachment_info(self, item_key: str) -> Dict:
        """获取附件详细信息"""
        try:
            item = self.get_item(item_key)
            links = item.get('links', {})
            attachment = links.get('attachment', {})

            return {
                'has_attachment': bool(attachment),
                'attachment_type': attachment.get('attachmentType'),
                'attachment_title': attachment.get('title'),
                'attachment_size': attachment.get('attachmentSize'),
                'href': attachment.get('href')
            }
        except Exception as e:
            return {'error': str(e)}

    def verify_file_integrity(self, item_key: str, local_path: str) -> bool:
        """验证下载文件的完整性"""
        try:
            # 获取原始文件 MD5
            original_md5 = self._calculate_md5(Path(local_path))

            # 可以与服务器端的 MD5 进行比较（如果 API 支持）
            return True  # 简化实现

        except Exception:
            return False
```

### 文件类型处理

```python
class FileTypeMixin(FilesMixin):
    """文件类型处理 Mixin"""

    def is_pdf(self, item_key: str) -> bool:
        """检查附件是否为 PDF"""
        try:
            href = self.get_item_attachment_href(item_key)
            return href.lower().endswith('.pdf') or 'application/pdf' in href.lower()
        except:
            return False

    def get_file_extension(self, item_key: str) -> str:
        """获取文件扩展名"""
        try:
            href = self.get_item_attachment_href(item_key)
            return os.path.splitext(href)[1].lower()
        except:
            return ''

    def filter_by_file_type(self, item_keys: List[str], file_type: str) -> List[str]:
        """按文件类型筛选条目"""
        filtered_keys = []

        for item_key in item_keys:
            try:
                if self.get_file_extension(item_key) == file_type.lower():
                    filtered_keys.append(item_key)
            except:
                continue

        return filtered_keys
```

### 进度跟踪

```python
class ProgressFilesMixin(FilesMixin):
    """带进度跟踪的文件操作 Mixin"""

    def download_with_progress(self, item_key: str, output_path: str,
                             progress_callback=None) -> str:
        """带进度跟踪的文件下载"""
        import requests

        # 获取文件信息
        attachment_info = self.get_attachment_info(item_key)
        file_size = attachment_info.get('attachment_size', 0)

        # 流式下载
        response = self._session.get(
            f"{self.base_url}/items/{item_key}/file",
            stream=True,
            params={"format": "raw"}
        )

        response.raise_for_status()

        downloaded = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback:
                        progress = (downloaded / file_size * 100) if file_size > 0 else 0
                        progress_callback(progress, downloaded, file_size)

        return output_path

    def upload_with_progress(self, file_path: str, parent_item: str = None,
                           progress_callback=None) -> Dict:
        """带进度跟踪的文件上传"""
        import os

        file_size = os.path.getsize(file_path)

        # 创建附件条目
        result = self.upload_file(file_path, parent_item)

        # 这里可以添加上传进度跟踪（需要特殊的 API 支持）
        return result
```

## 使用示例

### 基础文件操作

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# 下载附件
try:
    file_content = client.get_item_file("ITEM_KEY_HERE")
    with open("downloaded_file.pdf", "wb") as f:
        f.write(file_content.read())
    print("文件下载成功")
except Exception as e:
    print(f"下载失败: {e}")

# 复制到下载目录
dest_path = client.copy_attachment_to_downloads(
    "file:///Users/name/Zotero/storage/ABC123/paper.pdf"
)
print(f"文件已复制到: {dest_path}")
```

### 批量操作

```python
class ExtendedZoteroClient(ZoteroLocal, BatchFilesMixin):
    """扩展的 Zotero 客户端"""
    pass

client = ExtendedZoteroClient()

# 批量下载
item_keys = ["KEY1", "KEY2", "KEY3"]
downloaded = client.download_all_attachments(item_keys, "./downloads")

print(f"成功下载 {len(downloaded)} 个文件")
```

### 文件类型筛选

```python
class TypedZoteroClient(ZoteroLocal, FileTypeMixin):
    """支持文件类型处理的客户端"""
    pass

client = TypedZoteroClient()

# 只下载 PDF 文件
item_keys = ["KEY1", "KEY2", "KEY3", "KEY4"]
pdf_keys = client.filter_by_file_type(item_keys, ".pdf")
pdf_files = client.download_all_attachments(pdf_keys, "./pdfs")

print(f"下载了 {len(pdf_files)} 个 PDF 文件")
```

## 注意事项

1. **内存管理**: 大文件下载时注意内存使用，及时处理文件流
2. **文件权限**: 确保有足够的权限读取源文件和写入目标目录
3. **路径处理**: 使用 `Path` 对象处理跨平台路径差异
4. **错误恢复**: 实现适当的重试机制处理网络问题
5. **存储空间**: 监控磁盘空间，避免因空间不足导致上传/下载失败
6. **并发限制**: 避免同时进行大量文件操作，可能影响 Zotero 服务器性能

`FilesMixin` 提供了完整的文件管理功能，支持各种文件操作场景。