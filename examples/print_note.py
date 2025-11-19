from zoteroapi import ZoteroLocal, ZoteroLocalError
from typing import Dict, List
from pprint import pprint

def print_note_content(note: Dict) -> None:
    """Print the content of a note in a readable format"""
    data = note.get('data', {})
    print(f"Note Key: {note.get('key')}")
    print(f"Title: {data.get('title', 'Untitled Note')}")
    print(f"Content:\n{data.get('note', '')}\n")
    print("-" * 50)

def main(item_key: str):
    client = ZoteroLocal()
    
    try:

        
        # Example 2: Get all notes for a specific item
        
        item_notes = client.get_item_notes(item_key)
        
        print(f"\nFound {len(item_notes)} notes for item {item_key}:")
        for note in item_notes:
            print_note_content(note)
            
    except ZoteroLocalError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Replace with actual item key
    main(item_key = "H62SJYVX" ) 