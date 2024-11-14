from zoteroapi import ZoteroLocal
from typing import Dict, List
from pprint import pprint

def print_item_info(item: Dict) -> None:
    """Print basic information of the item"""
    data = item.get('data', {})
    print(f"\nTitle: {data.get('title', 'Untitled')}")
    print(f"Type: {data.get('itemType', 'Unknown type')}")
    print(f"Authors: {', '.join(c.get('name', '') for c in data.get('creators', []))}")
    if data.get('abstractNote'):
        print(f"Abstract: {data['abstractNote'][:200]}...")  # Only show the first 200 characters
    print(f"Tags: {', '.join(t.get('tag', '') for t in data.get('tags', []))}")
    print("-" * 50)

def search_demo():
    """Demonstrate the search functionality"""
    client = ZoteroLocal()
    
    try:
        # Search example
        search_terms = [
            "machine learning",  # Search for literature related to machine learning
            "uORF",  # Search for literature related to Python programming
        ]

        for term in search_terms:
            print(f"\nSearch keyword: '{term}'")
            results = client.search_items(term)
            
            if not results:
                print("No matching items found")
                continue
                
            print(f"Found {len(results)} matching items:")
            
            # Display detailed information for the first 3 results
            for item in results[:3]:
                print_item_info(item)
            
            if len(results) > 3:
                print(f"... {len(results) - 3} more results not displayed")

    except Exception as e:
        print(f"An error occurred during the search: {str(e)}")

# TBD
# def advanced_search_example():
#     """Demonstrate advanced search usage"""
#     client = ZoteroLocal()
    
#     try:
#         # Search for recently added items containing specific keywords
#         recent_papers = client.search_items("artificial intelligence")
        
#         # Filter by year
#         recent_ai_papers = [
#             item for item in recent_papers 
#             if item.get('data', {}).get('date', '').startswith('2023')
#         ]
        
#         print(f"\nAI-related papers published in 2023:")
#         for paper in recent_ai_papers:
#             print_item_info(paper)
            
#     except Exception as e:
#         print(f"An error occurred during the advanced search: {str(e)}")

def main():
    print("=== Basic Search Example ===")
    search_demo()
    
    # print("\n=== Advanced Search Example ===")
    # advanced_search_example()

if __name__ == "__main__":
    main() 