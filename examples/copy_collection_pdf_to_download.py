from zoteroapi import ZoteroLocal, ZoteroLocalError
from pathlib import Path
import os
import shutil

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
        
    # Set up download directory
    if download_dir:
        download_dir = Path(download_dir).absolute()
    else:
        download_dir = Path.home() / "Downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        items = client.get_collection_items(collection_key)
        success_count = 0
        
        for item in items:
            item_key = item.get('key')
            if not item_key:
                continue
                
            try:
                href = client.get_item_attachment_href(item_key)
                if not href:
                    continue
                
                file_path = client._normalize_path(href)
                if not os.path.exists(file_path):
                    continue
                
                # Copy file and rename if PMID exists
                dest_path = download_dir / os.path.basename(file_path)
                shutil.copy2(file_path, dest_path)
                
                pmid = client.get_pmid(item_key)
                if pmid:
                    new_path = download_dir / f"{pmid}.pdf"
                    dest_path.rename(new_path)
                
                success_count += 1
                    
            except ZoteroLocalError as e:
                print(f"Error processing item {item_key}: {e}")
        
        print(f"Successfully copied {success_count} out of {len(items)} items")
                
    except Exception as e:
        print(f"Failed to process collection: {e}")

if __name__ == "__main__":
    COLLECTION_NAME = "Oligo-FISH"  # Replace with your collection name
    DOWNLOAD_DIR = "../downloads"  # Replace with your desired download path
    copy_collection_pdfs(COLLECTION_NAME, DOWNLOAD_DIR)
