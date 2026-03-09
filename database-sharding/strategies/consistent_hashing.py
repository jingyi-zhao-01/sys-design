"""Consistent hashing with virtual nodes."""

import bisect
from typing import Any, List, Tuple
from .base import Shard, ShardingStrategy, KeyHasher


class ConsistentHashing(ShardingStrategy):
    """
    Consistent hashing with virtual nodes.

    Pros:
    - Minimal data movement when adding/removing shards
    - Better load distribution with virtual nodes
    - Good for dynamic scaling

    Cons:
    - More complex to implement
    - Slightly slower lookup O(log N) due to binary search
    """

    def __init__(
        self, shards: list = None, virtual_nodes: int = 100, hasher=KeyHasher.hash_md5
    ):
        super().__init__(shards or [])
        self.virtual_nodes = virtual_nodes
        self.hasher = hasher
        self._ring: List[Tuple[int, Shard]] = []  # (hash, shard)
        self._build_ring()

    def _hash(self, key: Any) -> int:
        """Generate a hash for the ring."""
        return self.hasher(key) % (2**32)

    def _build_ring(self) -> None:
        """Build the consistent hash ring with virtual nodes."""
        self._ring = []

        for shard in self.shards:
            for vn in range(self.virtual_nodes):
                # Create virtual node key: "shard_id-virtual_node_number"
                vn_key = f"{shard.shard_id}-{vn}"
                hash_value = self._hash(vn_key)
                bisect.insort(self._ring, (hash_value, shard))

    def get_shard(self, key: Any) -> Shard:
        if not self.shards:
            raise ValueError("No shards available")

        if not self._ring:
            self._build_ring()

        hash_value = self._hash(key)

        # Find the first shard with hash >= key hash
        # If not found, wrap around to the first shard
        indices = [i for i, (h, _) in enumerate(self._ring) if h >= hash_value]

        if indices:
            return self._ring[indices[0]][1]
        else:
            return self._ring[0][1]

    def add_shard(self, shard: Shard) -> None:
        """Add a new shard with virtual nodes."""
        self.shards.append(shard)
        self._build_ring()

    def remove_shard(self, shard_id: int) -> None:
        """Remove a shard and rebuild the ring."""
        self.shards = [s for s in self.shards if s.shard_id != shard_id]
        self._build_ring()

    def get_data_movement(self, old_shards: List[Shard]) -> float:
        """
        Calculate percentage of keys that would move when resharding.
        Useful for comparing strategies during rebalancing.
        """
        if not old_shards:
            return 100.0

        old_strategy = ConsistentHashing(old_shards, self.virtual_nodes, self.hasher)

        # Sample some keys to estimate movement
        test_keys = [f"user_{i}" for i in range(10000)]

        moved = 0
        for key in test_keys:
            old_shard = old_strategy.get_shard(key)
            new_shard = self.get_shard(key)
            if old_shard.shard_id != new_shard.shard_id:
                moved += 1

        return (moved / len(test_keys)) * 100
