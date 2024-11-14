from zoteroapi.client import ZoteroLocal, ZoteroLocalError

def main():
    # Initialize client
    zot = ZoteroLocal()
    
    try:
        print("=== Recent Items ===")
        # Get top-level items with limit
        items = zot.get_items_top(limit=10)
        
        if isinstance(items, list):
            for item in items:
                title = item.get('data', {}).get('title', 'Untitled')
                print(f"- {title}")
        else:
            print("No items found or invalid response format")

    except ZoteroLocalError as e:
        print(f"Error: API request failed: {str(e)}")
    except Exception as e:
        print(f"Unknown error: {str(e)}")

if __name__ == "__main__":
    main() 