from zoteroapi import ZoteroLocal, ZoteroLocalError
from typing import Dict

def print_item_info(item: Dict) -> None:
    """Print basic information about an item"""
    data = item.get('data', {})
    print(f"\nItem Key: {item.get('key', 'No key')}")
    print(f"Title: {data.get('title', 'Untitled')}")
    print(f"Type: {data.get('itemType', 'Unknown type')}")
    print(f"Authors: {', '.join(c.get('name', '') for c in data.get('creators', []))}")
    if data.get('abstractNote'):
        print(f"Abstract: {data['abstractNote'][:200]}...")  # Show first 200 chars
    print("-" * 50)

def main():
    client = ZoteroLocal()
    
    try:
        # Example 1: Partial match search
        title = "Establishment of single-cell transcriptional states during seed germination"
        # GB6GSMWC
        results = client.search_by_title(title)
        print(f"\nSearch results for title containing '{title}':")
        print(f"Found {len(results)} items:")
        for item in results:
            print_item_info(item)
            
        # Example 2: Exact match search
        exact_title = "A spatially resolved multi-omic single-cell atlas of soybean development"
        exact_results = client.search_by_title(exact_title, exact_match=True)
        print(f"\nExact match search for '{exact_title}':")
        print(f"Found {len(exact_results)} items:")
        for item in exact_results:
            print_item_info(item)
            
    except ZoteroLocalError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 