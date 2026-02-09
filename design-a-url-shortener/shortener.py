"""
URL Shortener Implementation

This module implements the core URL shortening service.
"""

from typing import Optional


class URLShortener:
    """
    A URL shortening service implementation.

    Features:
    - Generate short URLs from long URLs
    - Resolve short URLs to original URLs
    - Handle collisions
    - Track usage statistics
    """

    def __init__(self):
        """Initialize the URL shortener with storage."""
        self.url_map: dict[str, str] = {}
        self.reverse_map: dict[str, str] = {}
        self.counter: int = 0

    def shorten(self, long_url: str) -> str:
        """
        Create a shortened URL for the given long URL.

        Args:
            long_url: The original URL to shorten

        Returns:
            The shortened URL key
        """
        # TODO: Implement URL shortening logic
        pass

    def resolve(self, short_url: str) -> Optional[str]:
        """
        Resolve a short URL to its original long URL.

        Args:
            short_url: The shortened URL key

        Returns:
            The original long URL, or None if not found
        """
        # TODO: Implement URL resolution logic
        pass
