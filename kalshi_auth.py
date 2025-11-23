"""
Kalshi API RSA-PSS Authentication Module

This module handles RSA-PSS signature generation for Kalshi API authentication.
Kalshi requires RSA-PSS signing with SHA256 for all authenticated requests.

Usage:
    from kalshi_auth import load_private_key, sign_request
    
    private_key = load_private_key("path/to/private_key.pem")
    headers = sign_request(private_key, "GET", "/trade-api/v2/portfolio/balance", api_key_id="your-key-id")
"""

import base64
import time
from typing import Dict, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


def load_private_key(file_path: str) -> RSAPrivateKey:
    """
    Load an RSA private key from a PEM file.
    
    Args:
        file_path: Path to the PEM-encoded private key file
        
    Returns:
        RSAPrivateKey object
        
    Raises:
        FileNotFoundError: If the key file doesn't exist
        ValueError: If the key file is invalid or not a valid RSA key
    """
    try:
        with open(file_path, "rb") as key_file:
            key_data = key_file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Private key file not found: {file_path}")
    
    try:
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,  # Kalshi keys are typically not password-protected
            backend=default_backend()
        )
    except Exception as e:
        raise ValueError(f"Failed to load private key from {file_path}: {e}")
    
    if not isinstance(private_key, RSAPrivateKey):
        raise ValueError(f"Key file does not contain an RSA private key: {file_path}")
    
    return private_key


def sign_request(
    private_key: RSAPrivateKey,
    method: str,
    path: str,
    api_key_id: str,
    timestamp: Optional[int] = None
) -> Dict[str, str]:
    """
    Generate authentication headers for a Kalshi API request using RSA-PSS signing.
    
    Kalshi requires:
    - Message format: {timestamp}{method}{path}
    - Signature algorithm: RSA-PSS with SHA256
    - Headers: KALSHI-ACCESS-KEY, KALSHI-ACCESS-SIGNATURE, KALSHI-ACCESS-TIMESTAMP
    
    Args:
        private_key: RSA private key object
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        path: API endpoint path (e.g., "/trade-api/v2/portfolio/balance")
        api_key_id: Your Kalshi API key ID (from account settings)
        timestamp: Optional timestamp in milliseconds. If None, current time is used.
        
    Returns:
        Dictionary with authentication headers:
        {
            "KALSHI-ACCESS-KEY": "...",
            "KALSHI-ACCESS-SIGNATURE": "...",
            "KALSHI-ACCESS-TIMESTAMP": "..."
        }
    """
    if timestamp is None:
        timestamp = int(time.time() * 1000)  # Milliseconds since epoch
    
    timestamp_str = str(timestamp)
    
    # Create the message to sign: {timestamp}{method}{path}
    message = f"{timestamp_str}{method}{path}".encode('utf-8')
    
    # Sign using RSA-PSS with SHA256
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Base64 encode the signature
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    return {
        'KALSHI-ACCESS-KEY': api_key_id,
        'KALSHI-ACCESS-SIGNATURE': signature_b64,
        'KALSHI-ACCESS-TIMESTAMP': timestamp_str
    }

