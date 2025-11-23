"""
Kalshi API Authenticated HTTP Client

This module provides an async HTTP client for making authenticated requests to the Kalshi API.
It handles RSA-PSS signing automatically for all requests.

Usage:
    from kalshi_client import KalshiClient
    
    client = KalshiClient(
        api_key_id="your-api-key-id",
        private_key_path="path/to/private_key.pem",
        base_url="https://api.kalshi.com"
    )
    
    markets = await client.get("/trade-api/v2/markets")
"""

import httpx
from typing import Optional, Dict, Any
from kalshi_auth import load_private_key, sign_request


class KalshiClient:
    """
    Authenticated HTTP client for Kalshi API.
    
    Automatically signs all requests using RSA-PSS authentication.
    """
    
    def __init__(
        self,
        api_key_id: str,
        private_key_path: str,
        base_url: str = "https://api.kalshi.com"
    ):
        """
        Initialize the Kalshi client.
        
        Args:
            api_key_id: Your Kalshi API key ID (from account settings)
            private_key_path: Path to your RSA private key PEM file
            base_url: Base URL for Kalshi API (default: https://api.kalshi.com)
        """
        self.api_key_id = api_key_id
        self.base_url = base_url.rstrip('/')
        self.private_key = load_private_key(private_key_path)
    
    def _get_auth_headers(self, method: str, path: str) -> Dict[str, str]:
        """
        Generate authentication headers for a request.
        
        Args:
            method: HTTP method
            path: API endpoint path
            
        Returns:
            Dictionary of authentication headers
        """
        return sign_request(
            self.private_key,
            method,
            path,
            self.api_key_id
        )
    
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make an authenticated request to the Kalshi API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path (e.g., "/trade-api/v2/markets")
            params: Optional query parameters
            json: Optional JSON body for POST/PUT requests
            **kwargs: Additional arguments passed to httpx
            
        Returns:
            httpx.Response object
        """
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        # Generate authentication headers
        auth_headers = self._get_auth_headers(method, path)
        
        # Build full URL
        url = f"{self.base_url}{path}"
        
        # Make the request
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=auth_headers,
                params=params,
                json=json,
                **kwargs
            )
            return response
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """Make an authenticated GET request."""
        return await self.request("GET", path, params=params, **kwargs)
    
    async def post(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """Make an authenticated POST request."""
        return await self.request("POST", path, json=json, **kwargs)
    
    async def put(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        """Make an authenticated PUT request."""
        return await self.request("PUT", path, json=json, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """Make an authenticated DELETE request."""
        return await self.request("DELETE", path, **kwargs)

