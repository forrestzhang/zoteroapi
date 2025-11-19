# 文献集操作

本页面介绍如何管理 Zotero 文献集（Collections）。

## 获取所有文献集

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()

# 获取所有文献集
collections = client.get_collections()

print(f"共有 {len(collections)} 个文献集\n")

for collection in collections:
    data = collection.get('data', {})
    name = data.get('name', '未命名')
    num_items = data.get('numItems', 0)
    parent = data.get('parentCollection', False)
    
    # 显示层级结构
    indent = "  " if parent else ""
    print(f"{indent}📁 {name} ({num_items} 篇)")
```

## 获取单个文献集

```python
# 获取特定文献集的详细信息
collection_key = "COLL123"
collection = client.get_collection(collection_key)

data = collection.get('data', {})
print(f"名称: {data.get('name')}")
print(f"文献数: {data.get('numItems', 0)}")
```

## 获取文献集中的条目

```python
# 获取文献集中的所有条目
items = client.get_collection_items(collection_key)

print(f"\n文献集包含 {len(items)} 篇文献：\n")

for item in items:
    title = item.get('data', {}).get('title', '无标题')
    item_type = item.get('data', {}).get('itemType', 'unknown')
    print(f"  [{item_type}] {title}")
```

## 文献集数据结构

```python
{
    "key": "COLL123",
    "version": 45,
    "library": {...},
    "data": {
        "key": "COLL123",
        "version": 45,
        "name": "机器学习",
        "parentCollection": False,  # 或父文献集的 key
        "numItems": 25
    }
}
```

## 实用示例

### 显示文献集层级结构

```python
def display_collection_tree(client):
    """以树形结构显示文献集"""
    collections = client.get_collections()
    
    # 分离顶层和子文献集
    top_level = [c for c in collections 
                 if not c.get('data', {}).get('parentCollection')]
    children_map = {}
    
    for c in collections:
        parent = c.get('data', {}).get('parentCollection')
        if parent:
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(c)
    
    def print_tree(collection, level=0):
        data = collection.get('data', {})
        name = data.get('name', '未命名')
        num_items = data.get('numItems', 0)
        indent = "  " * level
        
        print(f"{indent}📁 {name} ({num_items})")
        
        # 打印子文献集
        coll_key = collection['key']
        if coll_key in children_map:
            for child in children_map[coll_key]:
                print_tree(child, level + 1)
    
    for coll in top_level:
        print_tree(coll)

# 使用
display_collection_tree(client)
```

### 导出文献集为 Markdown

```python
def export_collection_to_markdown(client, collection_key, output_file):
    """将文献集导出为 Markdown 文件"""
    collection = client.get_collection(collection_key)
    coll_name = collection.get('data', {}).get('name', '未命名')
    
    items = client.get_collection_items(collection_key)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {coll_name}\n\n")
        f.write(f"共 {len(items)} 篇文献\n\n")
        f.write("---\n\n")
        
        for i, item in enumerate(items, 1):
            data = item.get('data', {})
            title = data.get('title', '无标题')
            item_type = data.get('itemType', 'unknown')
            
            # 作者
            creators = data.get('creators', [])
            authors = ', '.join([
                f"{c.get('lastName', '')} {c.get('firstName', '')}"
                for c in creators
            ])
            
            date = data.get('date', '')
            doi = data.get('DOI', '')
            
            f.write(f"## {i}. {title}\n\n")
            f.write(f"- **类型**: {item_type}\n")
            if authors:
                f.write(f"- **作者**: {authors}\n")
            if date:
                f.write(f"- **日期**: {date}\n")
            if doi:
                f.write(f"- **DOI**: {doi}\n")
            f.write("\n---\n\n")
    
    print(f"已导出到 {output_file}")

# 使用
export_collection_to_markdown(client, "COLL123", "collection_export.md")
```

## 相关资源

- [文献条目管理](items-management.md)
- [搜索功能](search.md)
