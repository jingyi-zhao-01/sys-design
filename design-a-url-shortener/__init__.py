"""
URL Shortener System Design

Implements a URL shortening service similar to bit.ly or tinyurl.

Key components:
- URL encoding/decoding algorithms
- Hash collision handling
- Database schema for storing mappings
- API endpoints for creating and resolving short URLs
"""

from .shortener import URLShortener
from .encoder import encode_url, decode_url

__all__ = ["URLShortener", "encode_url", "decode_url"]
