from zoteroapi import ZoteroLocal
from typing import Dict, List
from pprint import pprint

def print_item_info(item: Dict) -> None:
    """打印条目的基本信息"""
    data = item.get('data', {})
    print(f"\n标题: {data.get('title', '无标题')}")
    print(f"类型: {data.get('itemType', '未知类型')}")
    print(f"作者: {', '.join(c.get('name', '') for c in data.get('creators', []))}")
    if data.get('abstractNote'):
        print(f"摘要: {data['abstractNote'][:200]}...")  # 只显示前200个字符
    print(f"标签: {', '.join(t.get('tag', '') for t in data.get('tags', []))}")
    print("-" * 50)

def search_demo():
    """演示搜索功能"""
    client = ZoteroLocal()
    
    try:
        # 搜索示例
        search_terms = [
            "machine learning",  # 搜索机器学习相关文献
            "uORF",  # 搜索Python编程相关文献

        ]

        for term in search_terms:
            print(f"\n搜索关键词: '{term}'")
            results = client.search_items(term)
            
            if not results:
                print("未找到匹配的条目")
                continue
                
            print(f"找到 {len(results)} 个匹配的条目:")
            
            # 显示前3个结果的详细信息
            for item in results[:3]:
                print_item_info(item)
            
            if len(results) > 3:
                print(f"... 还有 {len(results) - 3} 个结果未显示")

    except Exception as e:
        print(f"搜索过程中发生错误: {str(e)}")

def advanced_search_example():
    """演示高级搜索用法"""
    client = ZoteroLocal()
    
    try:
        # 搜索最近添加的包含特定关键词的条目
        recent_papers = client.search_items("artificial intelligence")
        
        # 按年份过滤
        recent_ai_papers = [
            item for item in recent_papers 
            if item.get('data', {}).get('date', '').startswith('2023')
        ]
        
        print(f"\n2023年发表的AI相关论文:")
        for paper in recent_ai_papers:
            print_item_info(paper)
            
    except Exception as e:
        print(f"高级搜索过程中发生错误: {str(e)}")

def main():
    print("=== 基础搜索示例 ===")
    search_demo()
    
    print("\n=== 高级搜索示例 ===")
    advanced_search_example()

if __name__ == "__main__":
    main() 