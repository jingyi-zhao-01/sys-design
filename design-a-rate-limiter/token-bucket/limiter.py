"""
Token Bucket Rate Limiter Implementation with common interface.

The token bucket algorithm works as follows:
- A bucket has a maximum capacity of tokens
- Tokens are added to the bucket at a fixed rate (refill rate)
- Each request consumes one or more tokens
- If sufficient tokens are available, the request is allowed and tokens are consumed
- If insufficient tokens are available, the request is denied
- Tokens are refilled continuously at the specified rate

This implementation is thread-safe and can be used in multi-threaded environments.
"""

import time
import threading
from typing import Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import RateLimiter, GlobalRateLimiter


class TokenBucket:
    """
    Thread-safe token bucket rate limiter.

    Args:
        capacity: Maximum number of tokens the bucket can hold
        refill_rate: Number of tokens added per second
        initial_tokens: Initial number of tokens (defaults to capacity)
    """

    def __init__(
        self, capacity: int, refill_rate: float, initial_tokens: Optional[int] = None
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = initial_tokens if initial_tokens is not None else capacity
        self.last_refill_time = time.time()
        self.lock = threading.Lock()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time since last refill."""
        now = time.time()
        elapsed = now - self.last_refill_time

        # Calculate tokens to add
        tokens_to_add = elapsed * self.refill_rate

        # Add tokens, but don't exceed capacity
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume the specified number of tokens.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were successfully consumed, False otherwise
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_available_tokens(self) -> float:
        """
        Get the current number of available tokens.

        Returns:
            Current number of tokens in the bucket
        """
        with self.lock:
            self._refill()
            return self.tokens

    def time_until_tokens_available(self, tokens: int = 1) -> float:
        """
        Calculate time until specified number of tokens will be available.

        Args:
            tokens: Number of tokens needed

        Returns:
            Time in seconds until tokens will be available (0 if already available)
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                return 0.0

            tokens_needed = tokens - self.tokens
            return tokens_needed / self.refill_rate


class TokenBucketRateLimiter(RateLimiter):
    """
    Token bucket rate limiter for multiple users implementing the RateLimiter interface.
    Each user has their own token bucket.

    Args:
        capacity: Maximum number of tokens per user
        refill_rate: Number of tokens added per second per user
    """

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = threading.Lock()

    def _get_bucket(self, user_id: str) -> TokenBucket:
        """Get or create a token bucket for a user."""
        with self.lock:
            if user_id not in self.buckets:
                self.buckets[user_id] = TokenBucket(self.capacity, self.refill_rate)
            return self.buckets[user_id]

    def allow_request(self, user_id: str, tokens: int = 1) -> bool:
        """
        Check if a request from a user should be allowed.

        Args:
            user_id: Unique identifier for the user
            tokens: Number of tokens to consume

        Returns:
            True if request is allowed, False otherwise
        """
        bucket = self._get_bucket(user_id)
        return bucket.consume(tokens)

    def get_user_stats(self, user_id: str) -> Dict[str, any]:
        """
        Get current rate limiting statistics for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing tokens available and wait time
        """
        bucket = self._get_bucket(user_id)
        return {
            "tokens_available": bucket.get_available_tokens(),
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
            "wait_time_for_1_token": bucket.time_until_tokens_available(1),
        }

    def get_wait_time(self, user_id: str, tokens: int = 1) -> float:
        """
        Get the time until tokens will be available for a user.

        Args:
            user_id: Unique identifier for the user
            tokens: Number of tokens needed

        Returns:
            Time in seconds until tokens available
        """
        bucket = self._get_bucket(user_id)
        return bucket.time_until_tokens_available(tokens)

    def reset_user(self, user_id: str) -> None:
        """
        Reset rate limiting state for a specific user.

        Args:
            user_id: Unique identifier for the user
        """
        with self.lock:
            if user_id in self.buckets:
                del self.buckets[user_id]

    def cleanup_inactive_users(self, inactive_threshold: float = 3600) -> int:
        """
        Remove buckets for users who haven't made requests recently.

        Args:
            inactive_threshold: Time in seconds after which a user is considered inactive

        Returns:
            Number of users removed
        """
        with self.lock:
            now = time.time()
            users_to_remove = []

            for user_id, bucket in self.buckets.items():
                if (now - bucket.last_refill_time) > inactive_threshold:
                    users_to_remove.append(user_id)

            for user_id in users_to_remove:
                del self.buckets[user_id]

            return len(users_to_remove)

    def get_algorithm_name(self) -> str:
        """Get the name of the rate limiting algorithm."""
        return "Token Bucket"

    def get_config(self) -> Dict[str, any]:
        """Get the configuration parameters of the rate limiter."""
        return {
            "algorithm": self.get_algorithm_name(),
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
            "active_users": len(self.buckets),
        }


class TokenBucketGlobalLimiter(GlobalRateLimiter):
    """
    Global token bucket rate limiter implementing the GlobalRateLimiter interface.

    Args:
        capacity: Maximum number of tokens the bucket can hold
        refill_rate: Number of tokens added per second
    """

    def __init__(self, capacity: int, refill_rate: float):
        self.bucket = TokenBucket(capacity, refill_rate)
        self.capacity = capacity
        self.refill_rate = refill_rate

    def allow_request(self, tokens: int = 1) -> bool:
        """
        Check if a request should be allowed globally.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if request is allowed, False otherwise
        """
        return self.bucket.consume(tokens)

    def get_stats(self) -> Dict[str, any]:
        """
        Get global rate limiting statistics.

        Returns:
            Dictionary containing global statistics
        """
        return {
            "tokens_available": self.bucket.get_available_tokens(),
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
        }

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time until request would be allowed.

        Args:
            tokens: Number of tokens needed

        Returns:
            Time in seconds until allowed
        """
        return self.bucket.time_until_tokens_available(tokens)


# Legacy compatibility - keep old classes for existing code
UserTokenBucket = TokenBucketRateLimiter
