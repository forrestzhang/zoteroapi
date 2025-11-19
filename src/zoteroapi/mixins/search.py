from typing import Dict, List
from ..exceptions import ZoteroLocalError

class SearchMixin:
    """Mixin class for search-related functionality"""
    
    def search_items(self, query: str) -> List[Dict]:
        """Search items by query string"""
        params = {"q": query}
        response = self._make_request("GET", "/items", params=params)
        return response.json()
        
    def search_by_doi(self, doi: str) -> List[Dict]:
        """Search items by DOI"""
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
        """Search items by PMID"""
        try:
            items = self.get_items()
            matching_items = []
            
            for item in items:
                extra = item.get('data', {}).get('extra', '')
                if extra:
                    for line in extra.split('\n'):
                        if line.startswith('PMID:') and line.split(':')[1].strip() == pmid:
                            matching_items.append(item)
                            break
                            
            return matching_items
        except Exception as e:
            raise ZoteroLocalError(f"Failed to search by PMID: {str(e)}")

    def search_by_title(self, title: str, exact_match: bool = False) -> List[Dict]:
        """
        Search items by title
        
        Args:
            title: The title to search for
            exact_match: If True, only return exact matches. If False, return partial matches.
            
        Returns:
            List of matching items
            
        Raises:
            ZoteroLocalError: If the search fails
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