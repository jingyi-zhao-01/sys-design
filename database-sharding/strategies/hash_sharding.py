"""Hash-based sharding strategy with buckets."""

from typing import Any, Dict
from .base import Shard, ShardingStrategy, KeyHasher


class HashSharding(ShardingStrategy):
    """
    Hash-based sharding with explicit buckets.

    Similar to modulo but with more control over the hash space.
    Uses a larger hash space to reduce collisions.
    """

    HASH_SPACE = 2**32  # 4 billion buckets

    def __init__(self, shards: list = None, hasher=KeyHasher.hash_md5):
        super().__init__(shards or [])
        self.hasher = hasher

    def get_shard(self, key: Any) -> Shard:
        if not self.shards:
            raise ValueError("No shards available")

        hash_value = self.hasher(key) % self.HASH_SPACE
        bucket_per_shard = self.HASH_SPACE // len(self.shards)
        shard_index = hash_value // bucket_per_shard
        return self.shards[min(shard_index, len(self.shards) - 1)]

    def add_shard(self, shard: Shard) -> None:
        self.shards.append(shard)

    def remove_shard(self, shard_id: int) -> None:
        self.shards = [s for s in self.shards if s.shard_id != shard_id]
