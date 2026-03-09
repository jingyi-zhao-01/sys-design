"""Modulo-based sharding strategy."""

from typing import Any
from .base import Shard, ShardingStrategy, KeyHasher


class ModuloSharding(ShardingStrategy):
    """
    Simple modulo-based partitioning.

    Pros:
    - Very simple to implement
    - O(1) lookup time

    Cons:
    - Adding/removing shards requires rebalancing ALL data
    - Uneven distribution if hash function doesn't distribute well
    """

    def __init__(self, shards: list = None, hasher=KeyHasher.hash_md5):
        super().__init__(shards or [])
        self.hasher = hasher

    def get_shard(self, key: Any) -> Shard:
        if not self.shards:
            raise ValueError("No shards available")

        hash_value = self.hasher(key)
        shard_index = hash_value % len(self.shards)
        return self.shards[shard_index]

    def add_shard(self, shard: Shard) -> None:
        self.shards.append(shard)

    def remove_shard(self, shard_id: int) -> None:
        self.shards = [s for s in self.shards if s.shard_id != shard_id]
