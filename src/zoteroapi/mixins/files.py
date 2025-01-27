from typing import Union, BinaryIO
from pathlib import Path
import os
import shutil
import platform
from urllib.parse import unquote
import zipfile
import io
from ..exceptions import ZoteroLocalError

class FilesMixin:
    """Mixin class for file-related operations"""
    
    def get_item_file(self, item_key: str) -> BinaryIO:
        """Get attachment file for an item"""
        response = self._make_request("GET", f"/items/{item_key}/file")
        
        if (response.headers.get('Content-Type') == 'application/zip' and
            response.headers.get('Zotero-File-Compressed') == 'Yes'):
            z = zipfile.ZipFile(io.BytesIO(response.content))
            return io.BytesIO(z.read(z.namelist()[0]))
        
        return io.BytesIO(response.content)
        
    def copy_attachment_to_downloads(self, file_uri: str, download_dir: str = None) -> str:
        """Copy attachment file to downloads directory"""
        try:
            file_path = self._normalize_path(file_uri)
            file_name = os.path.basename(file_path)
            
            if not download_dir:
                download_dir = str(Path.home() / "Downloads")
                
            os.makedirs(download_dir, exist_ok=True)
            dest_path = os.path.join(download_dir, file_name)
            
            shutil.copy2(file_path, dest_path)
            return dest_path
            
        except Exception as e:
            raise ZoteroLocalError(f"Failed to copy file: {str(e)}")
            
    def _normalize_path(self, file_uri: str) -> str:
        """Normalize file URI to system path"""
        if platform.system() == 'Windows':
            path = file_uri.replace('file:///', '')
        else:
            path = file_uri.replace('file://', '')
        
        path = unquote(path)
        return str(Path(path)) 