"""
Abstract base class for rate limiting algorithms.

This module defines the interface that all rate limiting algorithms must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class RateLimiter(ABC):
    """
    Abstract base class for rate limiting algorithms.

    All rate limiting implementations should inherit from this class and implement
    the required methods.
    """

    @abstractmethod
    def allow_request(self, user_id: str, tokens: int = 1) -> bool:
        """
        Check if a request should be allowed for the given user.

        Args:
            user_id: Unique identifier for the user
            tokens: Number of tokens/requests to consume (default: 1)

        Returns:
            True if the request should be allowed, False otherwise
        """
        pass

    @abstractmethod
    def get_user_stats(self, user_id: str) -> Dict[str, any]:
        """
        Get current rate limiting statistics for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing rate limit statistics (tokens, requests, etc.)
        """
        pass

    @abstractmethod
    def get_wait_time(self, user_id: str, tokens: int = 1) -> float:
        """
        Get the time in seconds until the request would be allowed.

        Args:
            user_id: Unique identifier for the user
            tokens: Number of tokens/requests needed

        Returns:
            Time in seconds until request would be allowed (0 if already allowed)
        """
        pass

    @abstractmethod
    def reset_user(self, user_id: str) -> None:
        """
        Reset rate limiting state for a specific user.

        Args:
            user_id: Unique identifier for the user
        """
        pass

    @abstractmethod
    def cleanup_inactive_users(self, inactive_threshold: float = 3600) -> int:
        """
        Remove rate limiting data for inactive users.

        Args:
            inactive_threshold: Time in seconds after which a user is considered inactive

        Returns:
            Number of users removed
        """
        pass

    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        Get the name of the rate limiting algorithm.

        Returns:
            Name of the algorithm (e.g., "Token Bucket", "Fixed Window")
        """
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, any]:
        """
        Get the configuration parameters of the rate limiter.

        Returns:
            Dictionary containing configuration parameters
        """
        pass


class GlobalRateLimiter(ABC):
    """
    Abstract base class for global rate limiting (across all users).
    """

    @abstractmethod
    def allow_request(self, tokens: int = 1) -> bool:
        """
        Check if a request should be allowed globally.

        Args:
            tokens: Number of tokens/requests to consume

        Returns:
            True if request is allowed, False otherwise
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, any]:
        """
        Get global rate limiting statistics.

        Returns:
            Dictionary containing global statistics
        """
        pass

    @abstractmethod
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time until request would be allowed.

        Args:
            tokens: Number of tokens needed

        Returns:
            Time in seconds until allowed (0 if already allowed)
        """
        pass
