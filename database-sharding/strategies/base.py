"""Base interfaces for database sharding strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib


@dataclass
class Shard:
    """Represents a single database shard."""

    shard_id: int
    host: str
    port: int
    database: str
    user: str
    password: str

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class ShardingStrategy(ABC):
    """Abstract base class for sharding strategies."""

    shards: List[Shard] = field(default_factory=list)

    @abstractmethod
    def get_shard(self, key: Any) -> Shard:
        """Determine which shard a key belongs to."""
        pass

    @abstractmethod
    def add_shard(self, shard: Shard) -> None:
        """Add a new shard to the cluster."""
        pass

    @abstractmethod
    def remove_shard(self, shard_id: int) -> None:
        """Remove a shard from the cluster."""
        pass

    def get_all_shards(self) -> List[Shard]:
        """Get all shards in the cluster."""
        return self.shards


class KeyHasher:
    """Utility class for hashing keys."""

    @staticmethod
    def hash_md5(key: Any) -> int:
        """Hash a key using MD5 and return an integer."""
        key_str = str(key)
        hash_obj = hashlib.md5(key_str.encode())
        return int(hash_obj.hexdigest(), 16)

    @staticmethod
    def hash_sha256(key: Any) -> int:
        """Hash a key using SHA-256 and return an integer."""
        key_str = str(key)
        hash_obj = hashlib.sha256(key_str.encode())
        return int(hash_obj.hexdigest(), 16)
