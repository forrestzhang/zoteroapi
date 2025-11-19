# ZoteroLocal

`ZoteroLocal` 是 ZoteroAPI 的主要客户端类，继承自 `BaseZoteroClient` 和所有 Mixin 类，提供了完整的 Zotero 本地服务器 API 功能。

## 类定义

```python
class ZoteroLocal(BaseZoteroClient, SearchMixin, FilesMixin, NotesMixin):
    """Zotero 本地 API 客户端"""
```

## 继承关系

- **BaseZoteroClient** - HTTP 请求处理和基础 API 功能
- **SearchMixin** - 搜索相关方法
- **FilesMixin** - 文件操作方法
- **NotesMixin** - 笔记管理方法

## 构造函数

```python
def __init__(self, base_url: str = "http://localhost:23119/api/users/000000/"):
    """
    初始化 ZoteroLocal 客户端

    Args:
        base_url: Zotero 本地服务器的基础 URL
                 默认: "http://localhost:23119/api/users/000000/"

    Examples:
        >>> client = ZoteroLocal()  # 使用默认配置
        >>> client = ZoteroLocal("http://localhost:23120/api/users/000000/")  # 自定义端口
    """
```

## 主要方法

### 文献条目管理

#### get_item()

```python
def get_item(self, item_key: str) -> Dict:
    """
    获取单个文献条目

    Args:
        item_key: 条目的唯一标识符（key）

    Returns:
        Dict: 包含完整条目信息的字典

    Raises:
        ZoteroLocalError: 当 API 请求失败时抛出
        ResourceNotFound: 当条目不存在时抛出

    Examples:
        >>> client = ZoteroLocal()
        >>> item = client.get_item("ABC123XYZ")
        >>> print(item['data']['title'])
        '深度学习研究'
    """
```

#### get_items()

```python
def get_items(self, limit: Optional[int] = None) -> List[Dict]:
    """
    获取所有文献条目

    Args:
        limit: 限制返回的条目数量。如果为 None，则返回所有条目

    Returns:
        List[Dict]: 条目列表，每个元素为包含完整条目信息的字典

    Warning:
        获取所有条目可能需要较长时间，建议使用 limit 参数
    """
```

#### get_items_top()

```python
def get_items_top(self, limit: int = 10) -> List[Dict]:
    """
    获取顶层条目（不包含子条目如笔记、附件）

    Args:
        limit: 限制返回的条目数量

    Returns:
        List[Dict]: 顶层条目列表
    """
```

#### get_item_by_key()

```python
def get_item_by_key(self, item_key: str) -> Dict:
    """
    通过 key 获取单个条目（get_item 的别名）

    Args:
        item_key: 条目的唯一标识符

    Returns:
        Dict: 条目信息
    """
```

### 文献集管理

#### get_collections()

```python
def get_collections(self) -> List[Dict]:
    """
    获取所有文献集

    Returns:
        List[Dict]: 文献集列表，每个元素包含：
            - key: 文献集唯一标识
            - data.name: 文献集名称
            - data.parentCollection: 父文献集 key
            - data.numItems: 包含的条目数量
    """
```

#### get_collection()

```python
def get_collection(self, collection_key: str) -> Dict:
    """
    获取单个文献集

    Args:
        collection_key: 文献集的唯一标识符

    Returns:
        Dict: 文献集信息
    """
```

#### get_collection_items()

```python
def get_collection_items(self, collection_key: str) -> List[Dict]:
    """
    获取文献集中的所有条目

    Args:
        collection_key: 文献集的唯一标识符

    Returns:
        List[Dict]: 条目列表
    """
```

### 标签管理

#### get_tags()

```python
def get_tags(self) -> List[str]:
    """
    获取所有标签

    Returns:
        List[str]: 标签列表
    """
```

### 文件操作

#### get_item_file()

```python
def get_item_file(self, item_key: str) -> BinaryIO:
    """
    获取条目的附件文件内容

    Args:
        item_key: 条目ID

    Returns:
        BinaryIO: 文件内容的二进制流对象

    Note:
        如果文件被压缩，会自动解压并返回第一个文件的内容
    """
```

#### download_file()

```python
def download_file(self, item_key: str, path: Union[str, Path]) -> None:
    """
    下载条目的附件文件到指定路径

    Args:
        item_key: 条目ID
        path: 保存路径

    Raises:
        ZoteroLocalError: 当下载失败时抛出
    """
```

#### upload_file()

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
    """
```

#### copy_attachment_to_downloads()

```python
def copy_attachment_to_downloads(self, file_uri: str, download_dir: str = None) -> str:
    """
    复制附件文件到下载目录

    Args:
        file_uri: 文件 URI（如 file:///path/to/file.pdf）
        download_dir: 目标下载目录（默认为用户下载目录）

    Returns:
        str: 复制后文件的完整路径

    Raises:
        ZoteroLocalError: 当复制失败时抛出
    """
```

#### get_item_attachment_href()

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
    """
```

### 笔记操作

#### get_note()

```python
def get_note(self, note_key: str) -> Dict:
    """
    通过笔记 key 获取笔记

    Args:
        note_key: 笔记的唯一标识符

    Returns:
        Dict: 包含完整笔记信息的字典
    """
```

#### get_item_notes()

```python
def get_item_notes(self, item_key: str) -> List[Dict]:
    """
    获取某个文献的所有笔记

    Args:
        item_key: 文献的唯一标识符

    Returns:
        List[Dict]: 笔记列表
    """
```

#### add_item_note()

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
    """
```

### 搜索功能

#### search_items()

```python
def search_items(self, query: str) -> List[Dict]:
    """
    通过关键词搜索文献条目

    Args:
        query: 搜索关键词字符串

    Returns:
        List[Dict]: 匹配的文献条目列表
    """
```

#### search_by_doi()

```python
def search_by_doi(self, doi: str) -> List[Dict]:
    """
    通过 DOI 搜索文献

    Args:
        doi: DOI 标识符，如 '10.1038/nature12373'

    Returns:
        List[Dict]: 匹配的文献列表（通常只有 0 个或 1 个结果）
    """
```

#### search_by_pmid()

```python
def search_by_pmid(self, pmid: str) -> List[Dict]:
    """
    通过 PubMed ID 搜索文献

    Args:
        pmid: PubMed ID 字符串

    Returns:
        List[Dict]: 匹配的文献列表
    """
```

#### search_by_title()

```python
def search_by_title(self, title: str, exact_match: bool = False) -> List[Dict]:
    """
    通过标题搜索文献

    Args:
        title: 要搜索的标题文本
        exact_match: 是否精确匹配（默认为模糊匹配）

    Returns:
        List[Dict]: 匹配的文献条目列表
    """
```

### 工具方法

#### get_pmid()

```python
def get_pmid(self, item_key: str) -> str:
    """
    获取文献的 PMID

    Args:
        item_key: Zotero 条目 key

    Returns:
        str: PMID 如果找到，否则返回空字符串
    """
```

## 使用示例

### 基础使用

```python
from zoteroapi import ZoteroLocal

# 创建客户端
client = ZoteroLocal()

# 获取最近文献
items = client.get_items_top(limit=10)
for item in items:
    print(f"- {item['data']['title']}")

# 搜索文献
results = client.search_items("machine learning")
print(f"找到 {len(results)} 篇相关文献")
```

### 文献集操作

```python
# 获取所有文献集
collections = client.get_collections()
for collection in collections:
    name = collection['data']['name']
    count = collection['data'].get('numItems', 0)
    print(f"{name}: {count} 篇")

# 获取特定文献集的内容
if collections:
    first_collection = collections[0]
    items = client.get_collection_items(first_collection['key'])
    print(f"文献集 '{first_collection['data']['name']}' 中的文献:")
    for item in items[:5]:
        print(f"- {item['data']['title']}")
```

### 文件操作

```python
# 下载附件
try:
    file_content = client.get_item_file("ITEM_KEY_HERE")
    with open("paper.pdf", "wb") as f:
        f.write(file_content.read())
    print("文件下载成功")
except Exception as e:
    print(f"下载失败: {e}")

# 复制文件到下载目录
dest_path = client.copy_attachment_to_downloads(
    "file:///Users/name/Zotero/storage/ABC123/paper.pdf"
)
print(f"文件已复制到: {dest_path}")
```

### 笔记管理

```python
# 获取文献的所有笔记
notes = client.get_item_notes("ITEM_KEY_HERE")
print(f"共有 {len(notes)} 条笔记")

for i, note in enumerate(notes, 1):
    content = note['data']['note']
    print(f"笔记 {i}: {content[:100]}...")

# 添加新笔记
new_note = client.add_item_note(
    "ITEM_KEY_HERE",
    "<p>这是一条新的笔记内容</p>",
    "我的笔记"
)
print(f"笔记已添加，key: {new_note['key']}")
```

### 搜索功能

```python
# 关键词搜索
results = client.search_items("深度学习")
print(f"找到 {len(results)} 篇相关文献")

# DOI 搜索
doi_results = client.search_by_doi("10.1038/nature12373")
if doi_results:
    print(f"找到文献: {doi_results[0]['data']['title']}")

# 标题搜索
title_results = client.search_by_title("机器学习", exact_match=False)
print(f"标题包含 '机器学习' 的文献: {len(title_results)} 篇")
```

## 错误处理

```python
from zoteroapi import ZoteroLocalError, ResourceNotFound

try:
    item = client.get_item("INVALID_KEY")
except ResourceNotFound:
    print("条目不存在")
except ZoteroLocalError as e:
    print(f"API 错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 注意事项

1. **连接要求**: 确保 Zotero 正在运行且本地服务器已启用
2. **权限**: 确保有足够的权限访问文件系统和网络
3. **性能**: 对于大型文献库，使用 `limit` 参数限制返回的条目数量
4. **内存**: 文件操作可能会占用大量内存，及时处理大文件
5. **HTML 格式**: 笔记内容使用 HTML 格式，注意转义特殊字符