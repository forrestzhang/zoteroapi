from zotero_local_api import ZoteroLocal, ZoteroLocalError
from typing import Dict, List
from pprint import pprint
import os

client = ZoteroLocal()

term = "uORF"
search_items_results = client.search_items(term)

item_keys = [item.get('key') for item in search_items_results]

for item_key in item_keys:
    try:
        href = client.get_item_attachment_href(item_key)
        download_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../downloads"))
        client.copy_attachment_to_downloads(href, download_dir=download_path)
        print(f"Successfully copied attachment for item {item_key}")
    except ZoteroLocalError as e:
        # Skip items without attachments or with errors
        print(f"Skipping item {item_key}: {str(e)}")
    except Exception as e:
        # Handle other unexpected errors
        print(f"Error processing item {item_key}: {str(e)}")
