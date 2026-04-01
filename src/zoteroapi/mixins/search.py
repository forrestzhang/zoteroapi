from typing import Dict, List
from ..exceptions import ZoteroLocalError

class SearchMixin:
    """搜索功能 Mixin 类。
    
    提供各种搜索方法，包括通用关键词搜索、DOI 搜索、PMID 搜索
    和标题搜索。该类通过 Mixin 模式混入到 ZoteroLocal 中。
    
    Note:
        此类不直接使用，而是通过 ZoteroLocal 类使用。
    """
    
    def search_items(self, query: str) -> List[Dict]:
        """通过关键词搜索文献条目。
        
        在文献库中搜索包含指定关键词的文献。搜索范围包括标题、
        摘要、标签等字段。
        
        Args:
            query: 搜索关键词字符串
            
        Returns:
            匹配的文献条目列表，每个元素为包含完整条目信息的字典
            
        Raises:
            ZoteroLocalError: 当 API 请求失败时抛出
            
        Examples:
            >>> client = ZoteroLocal()
            >>> results = client.search_items("machine learning")
            >>> print(f"找到 {len(results)} 篇相关文献")
            >>> for item in results[:5]:
            ...     title = item['data']['title']
            ...     print(f"  - {title}")
        """
        params = {"q": query}
        response = self._make_request("GET", "/items", params=params)
        return response.json()
        
    def search_by_doi(self, doi: str) -> List[Dict]:
        """通过 DOI 搜索文献。
        
        使用 DOI（数字对象标识符）精确查找文献。DOI 匹配不区分大小写。
        
        Args:
            doi: DOI 标识符，如 '10.1038/nature12373'
            
        Returns:
            匹配的文献列表（通常只有 0 个或 1 个结果）
            
        Raises:
            ZoteroLocalError: 当搜索失败时抛出
            
        Examples:
            >>> client = ZoteroLocal()
            >>> results = client.search_by_doi("10.1038/nature12373")
            >>> if results:
            ...     print(f"找到文献: {results[0]['data']['title']}")
            ... else:
            ...     print("未找到该 DOI 对应的文献")
        """
        try:
            items = self.get_items()
            matching_items = [
                item for item in items 
                if item.get('data', {}).get('DOI', '').lower() == doi.lower()
            ]
            return matching_items
        except Exception as e:
            raise ZoteroLocalError(f"Failed to search by DOI: {str(e)}")
            
    def search_by_pmid(self, pmid: str) -> List[Dict]:
        """通过 PMID 搜索文献。

        使用 PubMed ID 搜索医学文献。支持两种存储格式：
        - 新版 Zotero: 独立的 'PMID' 字段
        - 旧版 Zotero: 'extra' 字段中格式为 'PMID: 12345678'

        Args:
            pmid: PubMed ID 字符串

        Returns:
            匹配的文献列表

        Raises:
            ZoteroLocalError: 当搜索失败时抛出

        Examples:
            >>> client = ZoteroLocal()
            >>> results = client.search_by_pmid("12345678")
            >>> for item in results:
            ...     print(item['data']['title'])
        """
        try:
            items = self.get_items()
            matching_items = []

            for item in items:
                # 首先检查独立的 PMID 字段（新版 Zotero）
                item_pmid = item.get('data', {}).get('PMID')
                if item_pmid and item_pmid.strip() == pmid:
                    matching_items.append(item)
                    continue

                # 回退到 extra 字段（旧版 Zotero）
                extra = item.get('data', {}).get('extra', '')
                if extra:
                    for line in extra.split('\n'):
                        if line.startswith('PMID:'):
                            extracted_pmid = line.split(':', 1)[1].strip()
                            if extracted_pmid == pmid:
                                matching_items.append(item)
                            break

            return matching_items
        except Exception as e:
            raise ZoteroLocalError(f"Failed to search by PMID: {str(e)}")

    def search_by_title(self, title: str, exact_match: bool = False) -> List[Dict]:
        """通过标题搜索文献。

        根据文献标题进行搜索，支持精确匹配和模糊匹配。
        搜索不区分大小写。

        Args:
            title: 要搜索的标题文本
            exact_match: 是否精确匹配。True 表示只返回完全匹配的结果，
                        False 表示包含关键词即可（默认）

        Returns:
            匹配的文献条目列表

        Raises:
            ZoteroLocalError: 当搜索失败时抛出

        Examples:
            >>> client = ZoteroLocal()
            >>> # 模糊搜索标题包含 "深度学习" 的文献
            >>> results = client.search_by_title("深度学习")
            >>> print(f"找到 {len(results)} 篇相关文献")

            >>> # 精确搜索标题为 "机器学习基础" 的文献
            >>> results = client.search_by_title("机器学习基础", exact_match=True)
            >>> if results:
            ...     print(f"找到完全匹配的文献: {results[0]['data']['title']}")
        """
        try:
            # Get all items
            items = self.get_items()
            
            # Filter items by title
            matching_items = []
            for item in items:
                item_title = item.get('data', {}).get('title', '').lower()
                search_title = title.lower()
                
                if exact_match:
                    if item_title == search_title:
                        matching_items.append(item)
                else:
                    if search_title in item_title:
                        matching_items.append(item)
                        
            return matching_items
            
        except Exception as e:
            raise ZoteroLocalError(f"Failed to search by title: {str(e)}") 