"""Database router that routes queries to the correct shard."""

import psycopg2
from typing import Any, Optional, List, Dict
from contextlib import contextmanager
from strategies.base import Shard, ShardingStrategy


class ShardRouter:
    """Routes database operations to the correct shard based on sharding strategy."""

    def __init__(self, strategy: ShardingStrategy):
        self.strategy = strategy
        self._connections: Dict[int, psycopg2.extensions.connection] = {}

    def _get_connection(self, shard: Shard) -> psycopg2.extensions.connection:
        """Get or create a connection to the shard."""
        if shard.shard_id not in self._connections:
            self._connections[shard.shard_id] = psycopg2.connect(
                host=shard.host,
                port=shard.port,
                database=shard.database,
                user=shard.user,
                password=shard.password,
            )
        return self._connections[shard.shard_id]

    @contextmanager
    def get_shard_connection(self, key: Any):
        """Context manager for getting a connection to the shard for a key."""
        shard = self.strategy.get_shard(key)
        conn = self._get_connection(shard)
        try:
            yield conn, shard
        except Exception as e:
            conn.rollback()
            raise e

    def insert(
        self, table: str, key_field: str, key: Any, data: Dict[str, Any]
    ) -> None:
        """Insert a row into the correct shard."""
        with self.get_shard_connection(key) as (conn, shard):
            cursor = conn.cursor()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO {table} ({key_field}, {columns}) VALUES (%s, {placeholders})"
            cursor.execute(sql, (key, *data.values()))
            conn.commit()
            cursor.close()

    def select(
        self, table: str, key_field: str, key: Any, fields: List[str] = None
    ) -> Optional[Dict]:
        """Select a row from the correct shard."""
        with self.get_shard_connection(key) as (conn, shard):
            cursor = conn.cursor()
            fields_str = ", ".join(fields) if fields else "*"
            sql = f"SELECT {fields_str} FROM {table} WHERE {key_field} = %s"
            cursor.execute(sql, (key,))
            result = cursor.fetchone()
            cursor.close()

            if result and fields:
                return dict(zip(fields, result))
            elif result:
                return result
            return None

    def select_all_from_shard(self, shard_id: int) -> List[Dict]:
        """Get all records from a specific shard."""
        shard = next(
            (s for s in self.strategy.get_all_shards() if s.shard_id == shard_id), None
        )
        if not shard:
            return []

        conn = self._get_connection(shard)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        cursor.close()

        return results

    def get_distribution(self) -> Dict[int, int]:
        """Get the count of records in each shard."""
        distribution = {}
        for shard in self.strategy.get_all_shards():
            conn = self._get_connection(shard)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            distribution[shard.shard_id] = count
            cursor.close()
        return distribution

    def close_all(self):
        """Close all connections."""
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()
