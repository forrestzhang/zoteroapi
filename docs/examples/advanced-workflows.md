# 高级工作流示例

本文档展示了 ZoteroAPI 在实际研究工作中的应用场景和高级工作流。

## 研究项目管理

### 文献库整理工作流

```python
from zoteroapi import ZoteroLocal
import json
import os
from datetime import datetime

class ResearchProjectManager:
    """研究项目管理器"""

    def __init__(self):
        self.client = ZoteroLocal()

    def analyze_library_structure(self):
        """分析文献库结构"""
        collections = self.client.get_collections()
        items = self.client.get_items_top(limit=100)

        # 统计信息
        stats = {
            'total_collections': len(collections),
            'top_level_items': len(items),
            'collection_names': [col['data']['name'] for col in collections],
            'item_types': {}
        }

        # 统计文献类型
        for item in items:
            item_type = item['data'].get('itemType', 'unknown')
            stats['item_types'][item_type] = stats['item_types'].get(item_type, 0) + 1

        return stats

    def organize_by_year(self):
        """按年份组织文献"""
        items = self.client.get_items()
        year_groups = {}

        for item in items:
            data = item['data']
            date = data.get('date', '')
            title = data.get('title', 'untitled')

            # 提取年份
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            year = year_match.group() if year_match else '未知年份'

            if year not in year_groups:
                year_groups[year] = []

            year_groups[year].append({
                'title': title,
                'key': item['key'],
                'date': date,
                'item_type': data.get('itemType', 'unknown')
            })

        # 按年份排序
        sorted_years = sorted(year_groups.keys(), reverse=True)

        print("文献按年份分布:")
        for year in sorted_years:
            count = len(year_groups[year])
            print(f"  {year}: {count} 篇")

        return year_groups

    def find_duplicates(self):
        """查找重复文献"""
        items = self.client.get_items()
        title_map = {}

        for item in items:
            title = item['data'].get('title', '').lower().strip()
            if title:
                if title not in title_map:
                    title_map[title] = []
                title_map[title].append(item)

        # 找出重复项
        duplicates = {title: items for title, items in title_map.items() if len(items) > 1}

        if duplicates:
            print(f"发现 {len(duplicates)} 组重复文献:")
            for title, items in duplicates.items():
                print(f"\n重复标题: {title}")
                for item in items:
                    key = item['key']
                    creators = item['data'].get('creators', [])
                    if creators:
                        author = f"{creators[0].get('lastName', '')}, {creators[0].get('firstName', '')}"
                    else:
                        author = '未知作者'
                    print(f"  - {author} (Key: {key})")
        else:
            print("未发现重复文献")

        return duplicates

# 使用示例
manager = ResearchProjectManager()

# 分析文献库
stats = manager.analyze_library_structure()
print(f"文献库统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")

# 按年份组织
year_groups = manager.organize_by_year()

# 查找重复项
duplicates = manager.find_duplicates()
```

### 批量文献更新工作流

```python
class BatchLiteratureProcessor:
    """批量文献处理器"""

    def __init__(self):
        self.client = ZoteroLocal()

    def add_tags_to_recent_items(self, tag_prefix="2024_"):
        """为最近的文献添加标签"""
        import datetime

        current_year = datetime.datetime.now().year
        tag_name = f"{tag_prefix}{current_year}"

        # 获取最近的文献（这里模拟获取，实际需要根据日期筛选）
        recent_items = self.client.get_items_top(limit=50)

        processed_count = 0
        for item in recent_items:
            try:
                # 这里需要实现添加标签的功能
                # 注意：ZoteroAPI 可能需要更新来支持标签操作
                print(f"为文献 '{item['data']['title']}' 添加标签 '{tag_name}'")
                processed_count += 1

            except Exception as e:
                print(f"处理文献失败: {e}")

        print(f"成功处理 {processed_count} 篇文献")
        return processed_count

    def generate_literature_report(self, output_format="markdown"):
        """生成文献报告"""
        items = self.client.get_items_top(limit=100)
        collections = self.client.get_collections()

        report_content = f"# 文献报告\n\n"
        report_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 统计信息
        report_content += "## 统计信息\n\n"
        report_content += f"- 总文献数: {len(items)}\n"
        report_content += f"- 文献集数: {len(collections)}\n\n"

        # 文献类型分布
        type_count = {}
        for item in items:
            item_type = item['data'].get('itemType', 'unknown')
            type_count[item_type] = type_count.get(item_type, 0) + 1

        report_content += "### 文献类型分布\n\n"
        for item_type, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
            report_content += f"- {item_type}: {count}\n"

        # 最新文献
        report_content += "\n## 最新文献 (前20篇)\n\n"
        for i, item in enumerate(items[:20], 1):
            data = item['data']
            title = data.get('title', 'untitled')
            creators = data.get('creators', [])

            # 构建作者信息
            if creators:
                authors = ', '.join([f"{c['lastName']}, {c['firstName'][0]}"
                                   for c in creators[:3]])
                if len(creators) > 3:
                    authors += ' et al.'
            else:
                authors = '未知作者'

            publication = data.get('publicationTitle', '')
            date = data.get('date', '')

            report_content += f"{i}. **{title}**\n"
            report_content += f"   - 作者: {authors}\n"
            if publication:
                report_content += f"   - 期刊: {publication}\n"
            if date:
                report_content += f"   - 日期: {date}\n"
            report_content += "\n"

        # 保存报告
        filename = f"literature_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"文献报告已生成: {filename}")
        return filename

# 使用示例
processor = BatchLiteratureProcessor()

# 添加标签
# processor.add_tags_to_recent_items()

# 生成报告
report_file = processor.generate_literature_report()
```

## 学术写作工作流

### 参考文献格式化

```python
class ReferenceFormatter:
    """参考文献格式化器"""

    def __init__(self):
        self.client = ZoteroLocal()

    def format_apa_citation(self, item_key):
        """格式化为 APA 引用格式"""
        try:
            item = self.client.get_item(item_key)
            data = item['data']

            title = data.get('title', '')
            authors = data.get('creators', [])
            year = data.get('date', '')
            publication = data.get('publicationTitle', '')
            volume = data.get('volume', '')
            issue = data.get('issue', '')
            pages = data.get('pages', '')
            doi = data.get('DOI', '')

            # 提取年份
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', year)
            year = year_match.group() if year_match else ''

            # 格式化作者
            author_list = []
            for author in authors:
                if author.get('creatorType') == 'author':
                    last_name = author.get('lastName', '')
                    first_name = author.get('firstName', '')
                    if last_name and first_name:
                        author_list.append(f"{last_name}, {first_name[0]}.")

            if len(author_list) == 0:
                author_text = ""
            elif len(author_list) <= 7:
                author_text = " ".join(author_list)
            else:
                author_text = " ".join(author_list[:6]) + " ... " + author_list[-1]

            # 构建引用
            if author_text:
                citation = f"{author_text} ({year}). {title}."
            else:
                citation = f"{title} ({year})."

            if publication:
                citation += f" *{publication}*"

            if volume:
                citation += f", *{volume}*"
            if issue:
                citation += f"({issue})"

            if pages:
                citation += f", {pages}"

            if doi:
                citation += f". https://doi.org/{doi}"

            return citation

        except Exception as e:
            print(f"格式化引用失败: {e}")
            return None

    def generate_bibliography(self, item_keys, style="apa"):
        """生成参考文献列表"""
        bibliography = []

        for i, item_key in enumerate(item_keys, 1):
            if style.lower() == "apa":
                citation = self.format_apa_citation(item_key)
            else:
                citation = f"不支持的引用格式: {style}"

            if citation:
                bibliography.append(f"{i}. {citation}")

        return bibliography

    def export_bibliography(self, item_keys, filename="bibliography.txt", style="apa"):
        """导出参考文献到文件"""
        bibliography = self.generate_bibliography(item_keys, style)

        content = f"# 参考文献 ({style.upper()} 格式)\n\n"
        content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "\n".join(bibliography)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"参考文献已导出到: {filename}")
            return filename

        except Exception as e:
            print(f"导出失败: {e}")
            return None

# 使用示例
formatter = ReferenceFormatter()

# 格式化单个引用
# citation = formatter.format_apa_citation("ITEM_KEY_HERE")
# print(citation)

# 生成参考文献列表
item_keys = ["KEY1", "KEY2", "KEY3"]  # 替换为实际的 item keys
# bibliography = formatter.generate_bibliography(item_keys)

# 导出到文件
# formatter.export_bibliography(item_keys, "my_bibliography.txt")
```

### 文献综述工作流

```python
class LiteratureReviewWorkflow:
    """文献综述工作流"""

    def __init__(self):
        self.client = ZoteroLocal()

    def collect_papers_on_topic(self, topic, max_papers=50):
        """收集特定主题的文献"""
        print(f"收集关于 '{topic}' 的文献...")

        # 搜索相关文献
        search_results = self.client.search_items(topic)

        # 限制数量
        papers = search_results[:max_papers]

        print(f"找到 {len(papers)} 篇相关文献")

        # 按年份排序（最新的在前）
        def extract_year(item):
            date = item['data'].get('date', '')
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            return int(year_match.group()) if year_match else 0

        papers.sort(key=extract_year, reverse=True)

        return papers

    def extract_paper_info(self, papers):
        """提取文献信息"""
        paper_info = []

        for paper in papers:
            data = paper['data']

            info = {
                'key': paper['key'],
                'title': data.get('title', ''),
                'authors': [],
                'year': '',
                'journal': data.get('publicationTitle', ''),
                'abstract': data.get('abstractNote', ''),
                'doi': data.get('DOI', ''),
                'keywords': []
            }

            # 提取作者信息
            creators = data.get('creators', [])
            for creator in creators:
                if creator.get('creatorType') == 'author':
                    last_name = creator.get('lastName', '')
                    first_name = creator.get('firstName', '')
                    if last_name:
                        info['authors'].append(f"{last_name}, {first_name[0]}" if first_name else last_name)

            # 提取年份
            date = data.get('date', '')
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', date)
            info['year'] = year_match.group() if year_match else ''

            # 提取标签作为关键词
            tags = data.get('tags', [])
            info['keywords'] = [tag.get('tag', '') for tag in tags]

            paper_info.append(info)

        return paper_info

    def generate_review_outline(self, papers_info, topic):
        """生成文献综述大纲"""
        outline = f"# {topic} 文献综述\n\n"
        outline += f"## 概述\n\n"
        outline += f"本文综述了 {len(papers_info)} 篇关于 {topic} 的文献\n\n"

        # 按年份分组
        year_groups = {}
        for paper in papers_info:
            year = paper['year']
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(paper)

        # 时间线
        outline += "## 研究发展时间线\n\n"
        for year in sorted(year_groups.keys(), reverse=True):
            count = len(year_groups[year])
            outline += f"- **{year}**: {count} 篇文献\n"
        outline += "\n"

        # 主要期刊
        journals = {}
        for paper in papers_info:
            journal = paper['journal']
            if journal:
                journals[journal] = journals.get(journal, 0) + 1

        if journals:
            outline += "## 主要发表期刊\n\n"
            sorted_journals = sorted(journals.items(), key=lambda x: x[1], reverse=True)
            for journal, count in sorted_journals[:10]:
                outline += f"- {journal}: {count} 篇\n"
            outline += "\n"

        # 高频关键词
        all_keywords = []
        for paper in papers_info:
            all_keywords.extend(paper['keywords'])

        if all_keywords:
            from collections import Counter
            keyword_freq = Counter(all_keywords)

            outline += "## 高频关键词\n\n"
            for keyword, freq in keyword_freq.most_common(20):
                if keyword:
                    outline += f"- {keyword}: {freq} 次\n"
            outline += "\n"

        # 文献分类
        outline += "## 重点文献分析\n\n"
        for i, paper in enumerate(papers_info[:10], 1):  # 前10篇重点文献
            title = paper['title']
            authors = ', '.join(paper['authors'][:3])
            if len(paper['authors']) > 3:
                authors += ' et al.'

            outline += f"### {i}. {title}\n\n"
            outline += f"**作者:** {authors}\n"
            outline += f"**年份:** {paper['year']}\n"
            if paper['journal']:
                outline += f"**期刊:** {paper['journal']}\n"

            # 研究要点（这里需要根据实际情况填写）
            outline += "\n**研究要点:**\n"
            outline += "- [ ] 主要贡献\n"
            outline += "- [ ] 研究方法\n"
            outline += "- [ ] 关键发现\n\n"

        return outline

    def run_review_workflow(self, topic, max_papers=50):
        """运行完整的文献综述工作流"""
        print(f"开始 {topic} 的文献综述工作流...")

        # 1. 收集文献
        papers = self.collect_papers_on_topic(topic, max_papers)

        if not papers:
            print("未找到相关文献")
            return None

        # 2. 提取信息
        papers_info = self.extract_paper_info(papers)

        # 3. 生成大纲
        outline = self.generate_review_outline(papers_info, topic)

        # 4. 保存大纲
        filename = f"{topic.replace(' ', '_')}_review_outline.md"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(outline)

            print(f"文献综述大纲已生成: {filename}")
            return filename

        except Exception as e:
            print(f"保存失败: {e}")
            return None

# 使用示例
review_workflow = LiteratureReviewWorkflow()

# 运行文献综述工作流
# outline_file = review_workflow.run_review_workflow("machine learning", max_papers=30)
```

## 自动化监控工作流

### 新文献监控

```python
import time
from datetime import datetime, timedelta

class NewLiteratureMonitor:
    """新文献监控器"""

    def __init__(self, check_interval_hours=24):
        self.client = ZoteroLocal()
        self.check_interval = timedelta(hours=check_interval_hours)
        self.last_check_file = "last_check.txt"

    def load_last_check_time(self):
        """加载上次检查时间"""
        try:
            if os.path.exists(self.last_check_file):
                with open(self.last_check_file, 'r') as f:
                    timestamp = f.read().strip()
                    return datetime.fromisoformat(timestamp)
        except:
            pass
        return datetime.now() - timedelta(days=1)  # 默认检查前一天的文献

    def save_last_check_time(self):
        """保存检查时间"""
        try:
            with open(self.last_check_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            print(f"保存检查时间失败: {e}")

    def check_new_literature(self, keywords=None):
        """检查新文献"""
        last_check = self.load_last_check_time()

        # 获取最近添加的文献
        all_items = self.client.get_items_top(limit=100)
        new_items = []

        for item in all_items:
            data = item['data']
            added_date = data.get('dateAdded', '')

            # 解析添加日期
            try:
                item_date = datetime.fromisoformat(added_date.replace('Z', '+00:00'))
                if item_date > last_check.replace(tzinfo=item_date.tzinfo):
                    # 检查关键词匹配
                    if keywords:
                        title = data.get('title', '').lower()
                        abstract = data.get('abstractNote', '').lower()

                        if any(keyword.lower() in title or keyword.lower() in abstract
                               for keyword in keywords):
                            new_items.append(item)
                    else:
                        new_items.append(item)

            except:
                continue

        return new_items

    def send_notification(self, new_items, keywords):
        """发送新文献通知"""
        if not new_items:
            print("没有发现新文献")
            return

        subject = f"发现 {len(new_items)} 篇新文献"
        message = f"新文献通知 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n"

        if keywords:
            message += f"搜索关键词: {', '.join(keywords)}\n\n"

        message += "新文献列表:\n"
        for i, item in enumerate(new_items, 1):
            data = item['data']
            title = data.get('title', '')
            authors = data.get('creators', [])

            if authors:
                author_names = [f"{a.get('lastName', '')}" for a in authors[:3]]
                author_text = ', '.join(author_names)
                if len(authors) > 3:
                    author_text += ' et al.'
            else:
                author_text = '未知作者'

            message += f"\n{i}. {title}\n"
            message += f"   作者: {author_text}\n"

        print(f"\n{subject}")
        print("=" * len(subject))
        print(message)

        # 这里可以添加邮件发送、Slack 通知等
        return message

    def run_monitoring_cycle(self, keywords=None):
        """运行监控周期"""
        print(f"开始检查新文献... (关键词: {keywords or '全部'})")

        try:
            # 检查新文献
            new_items = self.check_new_literature(keywords)

            # 发送通知
            if new_items:
                self.send_notification(new_items, keywords)

            # 更新检查时间
            self.save_last_check_time()

        except Exception as e:
            print(f"监控检查失败: {e}")

    def start_monitoring(self, keywords=None, max_cycles=None):
        """开始持续监控"""
        print(f"开始文献监控 (检查间隔: {self.check_interval})")

        cycle_count = 0
        try:
            while max_cycles is None or cycle_count < max_cycles:
                self.run_monitoring_cycle(keywords)
                cycle_count += 1

                if max_cycles is None or cycle_count < max_cycles:
                    print(f"等待 {self.check_interval} 后进行下次检查...")
                    time.sleep(self.check_interval.total_seconds())

        except KeyboardInterrupt:
            print("\n监控已停止")
        except Exception as e:
            print(f"监控出错: {e}")

# 使用示例
monitor = NewLiteratureMonitor(check_interval_hours=1)

# 监控特定关键词的新文献
# monitor.start_monitoring(keywords=["machine learning", "deep learning"], max_cycles=3)

# 监控所有新文献
# monitor.start_monitoring(max_cycles=1)  # 只检查一次
```

## 小结

这些高级工作流展示了 ZoteroAPI 在实际研究中的强大应用：

1. **研究项目管理** - 文献库整理、重复检测、统计报告
2. **学术写作** - 参考文献格式化、引用生成
3. **文献综述** - 自动收集、信息提取、大纲生成
4. **自动化监控** - 新文献检测、关键词监控

通过这些工作流，你可以大幅提高研究效率和文献管理质量。