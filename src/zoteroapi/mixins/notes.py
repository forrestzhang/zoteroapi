from typing import Dict, List, Optional
from ..exceptions import ZoteroLocalError

class NotesMixin:
    """Mixin class for note-related functionality"""
    
    def get_note(self, note_key: str) -> Dict:
        """
        Get a note by its key
        
        Args:
            note_key: The key of the note to retrieve
            
        Returns:
            Dict containing the note data
            
        Raises:
            ZoteroLocalError: If the note cannot be retrieved or doesn't exist
        """
        try:
            response = self._make_request("GET", f"/items/{note_key}")
            item = response.json()
            
            # Verify this is actually a note
            if item.get('data', {}).get('itemType') != 'note':
                raise ZoteroLocalError("Retrieved item is not a note")
                
            return item
        except Exception as e:
            raise ZoteroLocalError(f"Failed to get note: {str(e)}")
            
    def get_item_notes(self, item_key: str) -> List[Dict]:
        """
        Get all notes attached to a specific item
        
        Args:
            item_key: The key of the parent item
            
        Returns:
            List of note objects
            
        Raises:
            ZoteroLocalError: If the notes cannot be retrieved
        """
        try:
            response = self._make_request("GET", f"/items/{item_key}/children")
            items = response.json()
            
            # Filter to only return notes
            notes = [
                item for item in items 
                if item.get('data', {}).get('itemType') == 'note'
            ]
            
            return notes
        except Exception as e:
            raise ZoteroLocalError(f"Failed to get item notes: {str(e)}")

    def add_item_note(self, item_key: str, note_text: str, title: Optional[str] = None) -> Dict:
        """
        Add a note to a specific item
        
        Args:
            item_key: The key of the parent item to attach the note to
            note_text: The content of the note in HTML format
            title: Optional title for the note
            
        Returns:
            The created note object
            
        Raises:
            ZoteroLocalError: If the note cannot be created
        """
        try:
            # Step 1: Create note template
            note_template = {
                "itemType": "note",
                "parentItem": item_key,
                "note": note_text,
                "tags": [],
                "collections": [],
                "relations": {}
            }
            
            if title:
                note_template["title"] = title
                
            # Step 2: Create the note
            create_response = self._make_request(
                "POST",
                "/items",
                data={"items": [note_template]},  # Wrap in items array
                headers={
                    "Content-Type": "application/json",
                }
            )
            
            result = create_response.json()
            
            # Step 3: Get and return the created note
            if "success" in result:
                success = result.get("success", {})
                if success:
                    new_note_key = next(iter(success.values()))
                    return self.get_note(new_note_key)
            
            raise ZoteroLocalError("Failed to create note: Invalid response")
            
        except Exception as e:
            raise ZoteroLocalError(f"Failed to add note to item: {str(e)}")
