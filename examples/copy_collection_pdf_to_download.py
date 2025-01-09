from zoteroapi import ZoteroLocal, ZoteroLocalError
from pathlib import Path
import os
import platform
import shutil
from urllib.parse import unquote

def get_collection_key_by_name(client: ZoteroLocal, collection_name: str) -> str:
    """
    Get collection key by searching for its name
    
    Args:
        client: ZoteroLocal client instance
        collection_name: Name of the collection to search for
        
    Returns:
        Collection key if found, None otherwise
    """
    collections = client.get_collections()
    
    for collection in collections:
        if collection.get('data', {}).get('name') == collection_name:
            return collection.get('key')
    
    return None

def normalize_path(file_uri: str) -> str:
    """
    Normalize file URI to system-specific path
    
    Args:
        file_uri: File URI (e.g., file:///Users/username/path/to/file.pdf)
        
    Returns:
        Normalized system path
    """
    # Remove 'file://' prefix and decode URL encoding
    if platform.system() == 'Windows':
        # Windows: Remove leading slash
        path = file_uri.replace('file:///', '')
    else:
        # macOS/Linux: Keep leading slash
        path = file_uri.replace('file://', '')
    
    # URL decode the path
    path = unquote(path)
    
    # Convert to Path object for proper handling
    return str(Path(path))

def copy_collection_pdfs(collection_name: str, download_dir: str = None) -> None:
    """
    Copy all PDF attachments from a Zotero collection to the downloads directory
    
    Args:
        collection_name: Name of the Zotero collection
        download_dir: Target download directory (default: user's Downloads folder)
    """
    client = ZoteroLocal()
    
    # Find collection key by name
    collection_key = get_collection_key_by_name(client, collection_name)
    if not collection_key:
        print(f"Collection '{collection_name}' not found")
        return
        
    print(f"Found collection: {collection_name} (key: {collection_key})")
    
    # Handle download directory path
    if download_dir:
        # Get the absolute path relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        download_dir = os.path.abspath(os.path.join(script_dir, download_dir))
    else:
        download_dir = str(Path.home() / "Downloads")
    
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    print(f"Using download directory: {download_dir}")
    
    try:
        # Get all items in the collection
        items = client.get_collection_items(collection_key)
        
        print(f"Found {len(items)} items in collection")
        success_count = 0
        
        for item in items:
            item_key = item.get('key')
            if not item_key:
                continue
                
            try:
                # Try to get PMID for filename
                pmid = client.get_pmid(item_key)
                
                # Get attachment href
                href = client.get_item_attachment_href(item_key)
                if not href:
                    print(f"Skipping item {item_key}: No PDF attachment found")
                    continue
                
                # Normalize the file path for the current OS
                file_path = normalize_path(href)
                print(f"Processing file: {file_path}")
                
                if not os.path.exists(file_path):
                    print(f"Skipping item {item_key}: File not found at {file_path}")
                    continue
                
                # Get original filename
                original_filename = os.path.basename(file_path)
                dest_path = os.path.join(download_dir, original_filename)
                print(f"Copying to: {dest_path}")
                
                # Copy file to downloads
                shutil.copy2(file_path, dest_path)
                
                # Rename using PMID if available
                if pmid:
                    new_filename = f"{pmid}.pdf"
                    new_path = os.path.join(download_dir, new_filename)
                    os.rename(dest_path, new_path)
                    print(f"Successfully copied and renamed attachment for item {item_key} to {new_filename}")
                else:
                    print(f"Successfully copied attachment for item {item_key} (no PMID available)")
                
                success_count += 1
                    
            except ZoteroLocalError as e:
                print(f"Skipping item {item_key}: {str(e)}")
            except Exception as e:
                print(f"Error processing item {item_key}: {str(e)}")
                import traceback
                print(traceback.format_exc())
        
        print(f"\nSummary: Successfully copied {success_count} out of {len(items)} items")
                
    except Exception as e:
        print(f"Failed to process collection: {str(e)}")

if __name__ == "__main__":
    # Example usage
    COLLECTION_NAME = "uORF"  # Replace with your collection name
    DOWNLOAD_DIR = "../downloads"  # Replace with your desired download path
    
    copy_collection_pdfs(COLLECTION_NAME, DOWNLOAD_DIR)
