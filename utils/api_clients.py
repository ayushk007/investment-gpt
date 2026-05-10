"""
API client utilities
"""

import requests
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """Utility class for API interactions"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """
        Make GET request
        
        Args:
            url: API endpoint URL
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response JSON
        """
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {"error": str(e)}
    
    def post(self, url: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """
        Make POST request
        
        Args:
            url: API endpoint URL
            data: Request body
            headers: Request headers
            
        Returns:
            Response JSON
        """
        try:
            response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {"error": str(e)}
    
    def close(self):
        """Close session"""
        self.session.close()
