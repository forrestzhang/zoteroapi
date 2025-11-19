from zoteroapi import ZoteroLocal, ZoteroLocalError
from typing import Dict

def print_note_info(note: Dict) -> None:
    """Print basic information about a note"""
    data = note.get('data', {})
    print(f"\nNote Key: {note.get('key')}")
    print(f"Title: {data.get('title', 'Untitled Note')}")
    print(f"Parent Item: {data.get('parentItem')}")
    print(f"Content:\n{data.get('note', '')}\n")
    print("-" * 50)

def main():
    client = ZoteroLocal()
    
    try:
        # Use a real item key from your library
        item_key = "GB6GSMWC"
        
        # Create and attach a note
        note = client.add_item_note(
            item_key=item_key,
            note_text="<p>Test note content</p>",
            title="Test Note Title"
        )
        
        # Print the result
        if note:
            print("\nNote created successfully:")
            print(f"Note Key: {note.get('key')}")
            print(f"Parent Item: {note.get('data', {}).get('parentItem')}")
            print(f"Title: {note.get('data', {}).get('title', 'Untitled')}")
            print(f"Content: {note.get('data', {}).get('note')}")
        
    except ZoteroLocalError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 