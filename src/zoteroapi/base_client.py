from typing import Dict, Optional, Any
import requests
from .exceptions import ZoteroLocalError, APIError, ResourceNotFound

class BaseZoteroClient:
    """Base client for making HTTP requests to Zotero API"""
    
    def __init__(self, base_url: str = "http://localhost:23119/api/users/000000/"):
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._cache = {}
        
    def _make_request(self, 
                     method: str, 
                     endpoint: str,  
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None,
                     headers: Optional[Dict] = None,
                     files: Optional[Dict] = None) -> requests.Response:
        """Send HTTP request to Zotero API"""
        url = f"{self.base_url}{endpoint}"
        
        params = params or {}
        if 'format' not in params:
            params['format'] = 'json'
            
        headers = headers or {}
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise ZoteroLocalError(f"API request failed: {str(e)}")
            
    def _request(self, 
                method: str,
                path: str,
                params: Optional[Dict] = None,
                data: Optional[Dict] = None,
                raw_response: bool = False,
                **kwargs) -> Any:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{path}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                **kwargs
            )
            response.raise_for_status()
            
            if raw_response:
                return response
            
            return response.json() if response.content else None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ResourceNotFound(f"Resource not found: {url}")
            raise APIError(f"Request failed: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}") 