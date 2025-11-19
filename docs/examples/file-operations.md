# 文件操作示例

本文档展示了如何使用 ZoteroAPI 进行文件下载、上传和管理操作。

## 下载附件文件

### 基础文件下载

```python
from zoteroapi import ZoteroLocal
import os

client = ZoteroLocal()

def download_attachment(item_key, save_path):
    """下载单个附件文件"""
    try:
        # 获取文件内容
        file_content = client.get_item_file(item_key)

        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 保存文件
        with open(save_path, 'wb') as f:
            f.write(file_content.read())

        print(f"文件已保存到: {save_path}")
        return save_path

    except Exception as e:
        print(f"下载失败: {e}")
        return None

# 使用示例
# download_attachment("ITEM_KEY_HERE", "./downloads/paper.pdf")
```

### 批量下载附件

```python
def download_all_attachments(collection_key=None, output_dir="./downloads"):
    """批量下载附件文件"""

    if collection_key:
        # 下载指定文献集的附件
        items = client.get_collection_items(collection_key)
        print(f"下载文献集中的附件...")
    else:
        # 下载所有顶层文献的附件
        items = client.get_items_top(limit=50)
        print(f"下载顶层文献的附件...")

    downloaded_files = []

    for item in items:
        item_key = item['key']
        item_title = item['data'].get('title', 'untitled')

        # 检查是否有附件
        links = item.get('links', {})
        if 'attachment' in links:
            try:
                # 获取附件信息
                attachment_info = links['attachment']
                attachment_title = attachment_info.get('title', 'attachment')

                # 清理文件名
                safe_title = "".join(c for c in item_title if c.isalnum() or c in (' ', '-', '_')).strip()
                if not safe_title:
                    safe_title = "untitled"

                # 构建文件名
                file_name = f"{safe_title}_{attachment_title}"
                file_path = os.path.join(output_dir, file_name)

                # 下载文件
                file_content = client.get_item_file(item_key)

                os.makedirs(output_dir, exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(file_content.read())

                downloaded_files.append(file_path)
                print(f"✓ 下载: {file_name}")

            except Exception as e:
                print(f"✗ 下载失败 ({item_title}): {e}")

    print(f"\n共下载 {len(downloaded_files)} 个文件")
    return downloaded_files

# 使用示例
# downloaded = download_all_attachments(output_dir="./my_papers")
```

### 下载 PDF 文件

```python
def download_pdf_files(item_keys, output_dir="./pdfs"):
    """专门下载 PDF 文件"""

    pdf_files = []

    for item_key in item_keys:
        try:
            # 获取文献信息
            item = client.get_item(item_key)
            title = item['data'].get('title', 'untitled')

            # 获取附件信息
            links = item.get('links', {})
            attachment = links.get('attachment', {})

            # 检查是否是 PDF
            if attachment.get('attachmentType') == 'application/pdf':
                # 生成安全的文件名
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                if not safe_title:
                    safe_title = "untitled"

                pdf_path = os.path.join(output_dir, f"{safe_title}.pdf")

                # 下载文件
                file_content = client.get_item_file(item_key)

                os.makedirs(output_dir, exist_ok=True)
                with open(pdf_path, 'wb') as f:
                    f.write(file_content.read())

                pdf_files.append(pdf_path)
                print(f"✓ PDF 下载完成: {safe_title}.pdf")
            else:
                print(f"- {title}: 不是 PDF 文件")

        except Exception as e:
            print(f"✗ 处理失败 ({item_key}): {e}")

    return pdf_files

# 使用示例
# item_list = ["KEY1", "KEY2", "KEY3"]
# pdfs = download_pdf_files(item_list)
```

## 文件管理

### 复制文件到下载目录

```python
def copy_to_downloads(file_path, custom_download_dir=None):
    """复制文件到下载目录"""
    try:
        # 构建文件 URI
        file_uri = f"file://{file_path}" if os.path.isabs(file_path) else f"file://{os.path.abspath(file_path)}"

        # 复制到下载目录
        dest_path = client.copy_attachment_to_downloads(file_uri, custom_download_dir)

        print(f"文件已复制到: {dest_path}")
        return dest_path

    except Exception as e:
        print(f"复制失败: {e}")
        return None

# 使用示例
# copy_to_downloads("/path/to/attachment.pdf", "/custom/download/dir")
```

### 文件大小检查

```python
import os

def check_file_sizes(download_dir):
    """检查下载文件的大小"""

    if not os.path.exists(download_dir):
        print(f"目录不存在: {download_dir}")
        return

    total_size = 0
    file_count = 0

    print("文件大小统计：")
    print("-" * 50)

    for filename in os.listdir(download_dir):
        file_path = os.path.join(download_dir, filename)

        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            file_count += 1

            # 格式化文件大小
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                size_str = f"{size/(1024*1024):.1f} MB"
            else:
                size_str = f"{size/(1024*1024*1024):.1f} GB"

            print(f"{filename:<30} {size_str:>10}")

    print("-" * 50)
    print(f"文件总数: {file_count}")
    print(f"总大小: {total_size/(1024*1024):.1f} MB")

# 使用示例
# check_file_sizes("./downloads")
```

### 文件类型分析

```python
import mimetypes
from collections import Counter

def analyze_file_types(directory):
    """分析下载文件的类型"""

    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return

    file_types = Counter()
    file_sizes = {}

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            # 获取 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                file_type = mime_type.split('/')[0]  # 主类型 (application, text, image 等)
            else:
                file_type = 'unknown'

            file_types[file_type] += 1

            # 记录文件大小
            size = os.path.getsize(file_path)
            if file_type not in file_sizes:
                file_sizes[file_type] = []
            file_sizes[file_type].append(size)

    print("文件类型分析：")
    print("-" * 40)

    for file_type, count in file_types.most_common():
        sizes = file_sizes[file_type]
        total_size = sum(sizes)
        avg_size = total_size / len(sizes)

        print(f"{file_type:<15} {count:>3} 个文件")
        print(f"{'':15} 总大小: {total_size/(1024*1024):.1f} MB")
        print(f"{'':15} 平均大小: {avg_size/(1024):.1f} KB")
        print()

# 使用示例
# analyze_file_types("./downloads")
```

## 高级文件操作

### 按条件下载

```python
def download_by_criteria(
    collection_key=None,
    years=None,
    file_type='pdf',
    max_files=100,
    output_dir="./filtered_downloads"
):
    """根据条件下载文件"""

    # 获取文献列表
    if collection_key:
        items = client.get_collection_items(collection_key)
        print(f"从文献集下载...")
    else:
        items = client.get_items_top(limit=max_files)
        print(f"从顶层文献下载...")

    downloaded_files = []

    for item in items:
        if len(downloaded_files) >= max_files:
            break

        try:
            data = item['data']
            title = data.get('title', 'untitled')

            # 年份筛选
            if years:
                date = data.get('date', '')
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', date)
                if not year_match or year_match.group() not in years:
                    continue

            # 检查附件
            links = item.get('links', {})
            if 'attachment' not in links:
                continue

            attachment = links['attachment']

            # 文件类型筛选
            if file_type == 'pdf' and attachment.get('attachmentType') != 'application/pdf':
                continue
            elif file_type == 'all':
                pass  # 下载所有类型
            else:
                continue

            # 下载文件
            item_key = item['key']
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            if not safe_title:
                safe_title = "untitled"

            file_content = client.get_item_file(item_key)

            # 确定文件扩展名
            if file_type == 'pdf':
                file_ext = '.pdf'
            else:
                # 尝试从附件标题获取扩展名
                attachment_title = attachment.get('title', '')
                if '.' in attachment_title:
                    file_ext = attachment_title[attachment_title.rfind('.'):]
                else:
                    file_ext = ''

            file_path = os.path.join(output_dir, f"{safe_title}{file_ext}")

            os.makedirs(output_dir, exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(file_content.read())

            downloaded_files.append(file_path)
            print(f"✓ 下载: {safe_title}{file_ext}")

        except Exception as e:
            print(f"✗ 跳过 ({title}): {e}")

    print(f"\n根据条件下载了 {len(downloaded_files)} 个文件")
    return downloaded_files

# 使用示例
# 下载 2020-2023 年的 PDF 文件
# recent_pdfs = download_by_criteria(years=['2020', '2021', '2022', '2023'], file_type='pdf')
```

### 下载进度跟踪

```python
import time
from tqdm import tqdm  # 需要安装: pip install tqdm

def download_with_progress(items, output_dir="./downloads"):
    """带进度条的批量下载"""

    downloaded_files = []
    failed_items = []

    print(f"开始下载 {len(items)} 个文件...")

    with tqdm(total=len(items), desc="下载进度") as pbar:
        for i, item in enumerate(items):
            try:
                item_key = item['key']
                title = item['data'].get('title', 'untitled')

                # 检查是否有附件
                if 'attachment' not in item.get('links', {}):
                    failed_items.append((title, "无附件"))
                    pbar.update(1)
                    continue

                # 生成文件名
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                if not safe_title:
                    safe_title = f"file_{i}"

                # 下载文件
                file_content = client.get_item_file(item_key)
                file_path = os.path.join(output_dir, f"{safe_title}.pdf")

                os.makedirs(output_dir, exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(file_content.read())

                downloaded_files.append(file_path)

                # 更新进度条
                pbar.set_postfix({"成功": len(downloaded_files), "失败": len(failed_items)})

            except Exception as e:
                failed_items.append((title, str(e)))

            pbar.update(1)

            # 添加小延迟避免过于频繁的请求
            time.sleep(0.1)

    print(f"\n下载完成！")
    print(f"成功: {len(downloaded_files)} 个文件")
    print(f"失败: {len(failed_items)} 个文件")

    if failed_items:
        print("\n失败的文件：")
        for title, error in failed_items[:5]:  # 只显示前 5 个
            print(f"  {title}: {error}")

    return downloaded_files, failed_items

# 使用示例
# items = client.get_items_top(limit=20)
# success, failed = download_with_progress(items)
```

## 文件验证

### 检查下载完整性

```python
import hashlib

def verify_file_integrity(file_path, expected_size=None):
    """验证文件完整性"""

    if not os.path.exists(file_path):
        return False, "文件不存在"

    # 检查文件大小
    actual_size = os.path.getsize(file_path)
    if expected_size and actual_size != expected_size:
        return False, f"文件大小不匹配: 期望 {expected_size}, 实际 {actual_size}"

    # 检查文件是否为空
    if actual_size == 0:
        return False, "文件为空"

    # 检查 PDF 文件头
    if file_path.lower().endswith('.pdf'):
        try:
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    return False, "PDF 文件头不正确"
        except Exception as e:
            return False, f"无法读取 PDF 文件头: {e}"

    return True, "文件完整"

def batch_verify_files(directory):
    """批量验证下载的文件"""

    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    valid_files = []
    invalid_files = []

    print(f"验证 {len(files)} 个文件...")

    for filename in files:
        file_path = os.path.join(directory, filename)
        is_valid, message = verify_file_integrity(file_path)

        if is_valid:
            valid_files.append(filename)
        else:
            invalid_files.append((filename, message))
            print(f"❌ {filename}: {message}")

    print(f"\n验证完成:")
    print(f"✓ 有效文件: {len(valid_files)}")
    print(f"✗ 无效文件: {len(invalid_files)}")

    return valid_files, invalid_files

# 使用示例
# valid, invalid = batch_verify_files("./downloads")
```

## 小结

- 使用 `get_item_file()` 下载附件文件内容
- 实现批量下载和条件下载功能
- 添加进度跟踪和错误处理
- 验证下载文件的完整性
- 分析和管理下载的文件

这些示例可以帮助你有效地管理 Zotero 中的附件文件。