"""No sharding strategy - single database baseline."""

from typing import Any, List
from .base import Shard, ShardingStrategy


class NoSharding(ShardingStrategy):
    """
    No sharding - single database baseline.

    This is useful for comparison and small-scale deployments.
    All data goes to a single shard.

    Pros:
    - Simple to implement
    - No cross-shard queries needed
    - ACID transactions across all data

    Cons:
    - No horizontal scaling
    - Single point of failure
    - Limited by single node capacity
    """

    def __init__(self, shards: list = None):
        # Only use the first shard, ignore the rest
        super().__init__(shards[:1] if shards else [])

    def get_shard(self, key: Any) -> Shard:
        if not self.shards:
            raise ValueError("No shards available")
        # Always return the single shard
        return self.shards[0]

    def add_shard(self, shard: Shard) -> None:
        # In no-sharding mode, we ignore additional shards
        # Only keep the first one
        if not self.shards:
            self.shards.append(shard)

    def remove_shard(self, shard_id: int) -> None:
        # Only remove if it's the primary shard
        if self.shards and self.shards[0].shard_id == shard_id:
            self.shards = []

    def get_data_movement(self, old_shards: List[Shard]) -> float:
        """No data movement since all data stays on single shard."""
        return 0.0
