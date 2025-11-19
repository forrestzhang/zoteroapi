# 标签管理

标签是 Zotero 中组织和管理文献的重要工具。本章介绍如何使用 ZoteroAPI 进行标签的各种操作。

## 获取所有标签

使用 `get_tags()` 方法获取文献库中的所有标签：

```python
from zoteroapi import ZoteroLocal

client = ZoteroLocal()
tags = client.get_tags()

print(f"共有 {len(tags)} 个标签:")
for tag in tags[:10]:  # 显示前 10 个标签
    print(f"- {tag}")
```

## 标签分析

对标签进行分析和统计：

```python
from collections import Counter

# 获取所有标签
tags = client.get_tags()

# 标签统计
tag_count = Counter(tags)
print(f"最常用的 10 个标签:")
for tag, count in tag_count.most_common(10):
    print(f"{tag}: {count} 次")

# 标签长度分析
tag_lengths = [len(tag) for tag in tags]
avg_length = sum(tag_lengths) / len(tag_lengths)
print(f"平均标签长度: {avg_length:.1f} 字符")
```

## 按标签筛选文献

虽然 ZoteroAPI 没有直接的按标签搜索方法，但可以通过获取所有文献然后筛选：

```python
def get_items_by_tag(tag_name: str) -> list:
    """获取指定标签的所有文献"""
    items = client.get_items()
    matching_items = []

    for item in items:
        tags = item.get('data', {}).get('tags', [])
        item_tag_names = [tag.get('tag', '') for tag in tags]

        if tag_name in item_tag_names:
            matching_items.append(item)

    return matching_items

# 示例：获取带有 "机器学习" 标签的文献
ml_items = get_items_by_tag("机器学习")
print(f"找到 {len(ml_items)} 篇带有 '机器学习' 标签的文献")

for item in ml_items[:5]:
    title = item['data']['title']
    print(f"- {title}")
```

## 标签管理实用函数

### 清理重复标签

```python
def clean_duplicate_tags() -> dict:
    """清理重复的标签（忽略大小写）"""
    tags = client.get_tags()
    normalized_tags = {}

    for tag in tags:
        normalized = tag.lower().strip()
        if normalized not in normalized_tags:
            normalized_tags[normalized] = []
        normalized_tags[normalized].append(tag)

    # 找出重复的标签
    duplicates = {k: v for k, v in normalized_tags.items() if len(v) > 1}

    if duplicates:
        print("发现重复的标签：")
        for normalized, variants in duplicates.items():
            print(f"  {normalized}: {', '.join(variants)}")
    else:
        print("没有发现重复的标签")

    return duplicates
```

### 标签重命名建议

```python
def suggest_tag_merges() -> dict:
    """建议可以合并的相似标签"""
    tags = client.get_tags()
    suggestions = {}

    # 简单的相似性检测（基于编辑距离）
    from difflib import SequenceMatcher

    for i, tag1 in enumerate(tags):
        for tag2 in tags[i+1:]:
            similarity = SequenceMatcher(None, tag1.lower(), tag2.lower()).ratio()
            if similarity > 0.8:  # 相似度阈值
                key = tuple(sorted([tag1, tag2]))
                suggestions[key] = similarity

    # 按相似度排序
    sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)

    if sorted_suggestions:
        print("建议合并的相似标签：")
        for (tag1, tag2), similarity in sorted_suggestions[:10]:
            print(f"  '{tag1}' 和 '{tag2}' (相似度: {similarity:.2f})")

    return sorted_suggestions
```

## 标签统计报告

```python
def generate_tag_report():
    """生成详细的标签统计报告"""
    tags = client.get_tags()
    items = client.get_items()

    # 统计每个标签的使用次数
    tag_usage = {}
    for item in items:
        item_tags = item.get('data', {}).get('tags', [])
        for tag_info in item_tags:
            tag_name = tag_info.get('tag', '')
            tag_usage[tag_name] = tag_usage.get(tag_name, 0) + 1

    # 排序
    sorted_tags = sorted(tag_usage.items(), key=lambda x: x[1], reverse=True)

    print("=" * 50)
    print("标签统计报告")
    print("=" * 50)
    print(f"总标签数: {len(tags)}")
    print(f"总文献数: {len(items)}")
    print(f"有标签的文献数: {len([i for i in items if i.get('data', {}).get('tags')])}")
    print()

    print("前 20 个最常用标签:")
    print("-" * 30)
    for i, (tag, count) in enumerate(sorted_tags[:20], 1):
        print(f"{i:2d}. {tag:<20} {count:>4} 次")

    print()
    print("标签使用分布:")
    print("-" * 20)

    # 使用分布统计
    usage_ranges = [
        (1, "1次"),
        (2, "2-5次"),
        (6, "6-10次"),
        (11, "11-20次"),
        (21, "20+次")
    ]

    for threshold, label in usage_ranges:
        if threshold == 1:
            count = len([t for t, c in sorted_tags if c == threshold])
        elif threshold == 2:
            count = len([t for t, c in sorted_tags if 2 <= c <= 5])
        elif threshold == 6:
            count = len([t for t, c in sorted_tags if 6 <= c <= 10])
        elif threshold == 11:
            count = len([t for t, c in sorted_tags if 11 <= c <= 20])
        else:
            count = len([t for t, c in sorted_tags if c >= 21])

        print(f"{label:<10} {count:>4} 个标签")

# 生成报告
generate_tag_report()
```

## 标签可视化

使用 matplotlib 创建标签云（需要安装 matplotlib）：

```python
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def create_tag_cloud():
    """创建标签云图"""
    tags = client.get_tags()
    items = client.get_items()

    # 统计标签使用次数
    tag_counts = {}
    for item in items:
        for tag_info in item.get('data', {}).get('tags', []):
            tag = tag_info.get('tag', '')
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # 创建词云
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        font_path='simhei.ttf',  # 中文字体路径
        max_words=100
    ).generate_from_frequencies(tag_counts)

    # 显示图像
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Zotero 标签云')
    plt.tight_layout()
    plt.show()

# 创建标签云（需要安装 wordcloud 和 matplotlib）
# create_tag_cloud()
```

## 标签管理最佳实践

### 1. 标签命名规范

```python
# 好的标签示例
good_tags = [
    "机器学习",
    "深度学习",
    "计算机视觉",
    "自然语言处理",
    "2024-论文",
    "必读"
]

# 避免的标签示例
bad_tags = [
    "ml",           # 缩写
    "PAPER",        # 全大写
    "  机器学习  ",  # 前后空格
    "机器学习!@#"   # 特殊字符
]
```

### 2. 标签层次结构

虽然 Zotero 不支持嵌套标签，但可以使用命名约定来模拟层次：

```python
hierarchical_tags = [
    "方法/监督学习",
    "方法/无监督学习",
    "方法/强化学习",
    "应用/计算机视觉",
    "应用/自然语言处理",
    "状态/已读",
    "状态/待读",
    "状态/重要"
]
```

### 3. 标签检查函数

```python
def validate_tags():
    """验证标签质量"""
    tags = client.get_tags()
    issues = []

    for tag in tags:
        # 检查空格
        if tag != tag.strip():
            issues.append(f"包含前后空格: '{tag}'")

        # 检查特殊字符
        if any(char in tag for char in '!@#$%^&*()+=[]{}|\\:";\'<>?,./'):
            issues.append(f"包含特殊字符: '{tag}'")

        # 检查纯大写
        if tag.isupper() and len(tag) > 2:
            issues.append(f"全大写: '{tag}'")

        # 检查过短
        if len(tag.strip()) < 2:
            issues.append(f"过短: '{tag}'")

    if issues:
        print(f"发现 {len(issues)} 个标签问题：")
        for issue in issues[:10]:  # 只显示前 10 个
            print(f"  {issue}")
    else:
        print("所有标签看起来都很正常！")

    return issues

# 验证标签
validate_tags()
```

## 小结

- 使用 `get_tags()` 获取所有标签
- 通过筛选文献实现按标签查找
- 定期清理重复和相似的标签
- 建立统一的标签命名规范
- 使用统计和可视化工具分析标签使用情况