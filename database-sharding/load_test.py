#!/usr/bin/env python3
"""
Load test demo for database sharding strategies.
Demonstrates how sharding handles high traffic better than no-sharding.
"""

import argparse
import time
import random
import string
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from strategies.base import Shard
from strategies.modulo_sharding import ModuloSharding
from strategies.hash_sharding import HashSharding
from strategies.consistent_hashing import ConsistentHashing
from strategies.no_sharding import NoSharding
from router import ShardRouter


def create_test_shards(count: int = 4) -> List[Shard]:
    """Create test shard configurations."""
    shards = []
    base_port = 5432
    for i in range(count):
        shards.append(
            Shard(
                shard_id=i + 1,
                host="localhost",
                port=base_port + i,
                database=f"shard{i + 1}",
                user="sharding",
                password="sharding123",
            )
        )
    return shards


def init_database(router: ShardRouter):
    """Initialize the database schema."""
    print("  Initializing database schema...")

    # Create table in each shard
    for shard in router.strategy.get_all_shards():
        conn = router._get_connection(shard)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        cursor.close()

    print("  Schema initialized.")


def generate_users(count: int) -> List[Dict]:
    """Generate random user data."""
    users = []
    for i in range(count):
        users.append(
            {
                "user_id": f"user_{i:06d}",
                "username": f"user{i}",
                "email": f"user{i}@example.com",
            }
        )
    return users


def insert_users(router: ShardRouter, users: List[Dict]) -> Tuple[int, float]:
    """Insert users and return (count, duration)."""
    start = time.time()
    success = 0

    for user in users:
        try:
            router.insert(
                "users",
                "user_id",
                user["user_id"],
                {"username": user["username"], "email": user["email"]},
            )
            success += 1
        except Exception as e:
            pass  # Ignore duplicates

    duration = time.time() - start
    return success, duration


def read_users(
    router: ShardRouter, user_ids: List[str], num_threads: int = 10
) -> Tuple[int, float]:
    """Read users concurrently and return (count, duration)."""
    start = time.time()
    success = 0
    errors = 0

    def read_single(user_id):
        try:
            result = router.select("users", "user_id", user_id, ["user_id"])
            return 1 if result else 0
        except Exception:
            return 0

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(read_single, uid) for uid in user_ids]
        for future in as_completed(futures):
            result = future.result()
            if result:
                success += 1
            else:
                errors += 1

    duration = time.time() - start
    return success, duration


def run_load_test(
    strategy_name: str,
    shards: List[Shard],
    num_users: int = 1000,
    num_reads: int = 5000,
    num_threads: int = 20,
):
    """Run load test for a specific strategy."""
    print(f"\n{'=' * 60}")
    print(f"  Load Test: {strategy_name}")
    print(f"{'=' * 60}")

    # Create strategy
    if strategy_name == "no-sharding":
        strategy = NoSharding(shards)
    elif strategy_name == "modulo":
        strategy = ModuloSharding(shards)
    elif strategy_name == "hash":
        strategy = HashSharding(shards)
    elif strategy_name == "consistent":
        strategy = ConsistentHashing(shards)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    # Create router
    router = ShardRouter(strategy)

    # Initialize database
    init_database(router)

    # Generate test users
    users = generate_users(num_users)
    user_ids = [u["user_id"] for u in users]

    # Insert users
    print(f"\n  Inserting {num_users} users...")
    inserted, insert_time = insert_users(router, users)
    insert_rate = inserted / insert_time if insert_time > 0 else 0
    print(f"  Inserted: {inserted} in {insert_time:.2f}s ({insert_rate:.1f} ops/sec)")

    # Warm up - read all users once
    print(f"\n  Warming up cache...")
    for uid in user_ids[:100]:
        try:
            router.select("users", "user_id", uid, ["user_id"])
        except:
            pass

    # Concurrent read test
    print(f"\n  Running concurrent reads ({num_reads} reads, {num_threads} threads)...")

    # Measure latencies
    latencies = []
    lock = threading.Lock()

    def timed_read(user_id):
        start = time.time()
        try:
            result = router.select("users", "user_id", user_id, ["user_id"])
            latency = (time.time() - start) * 1000  # ms
            with lock:
                latencies.append(latency)
            return 1 if result else 0
        except Exception as e:
            latency = (time.time() - start) * 1000
            with lock:
                latencies.append(latency)
            return 0

    start = time.time()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(timed_read, random.choice(user_ids))
            for _ in range(num_reads)
        ]
        results = [f.result() for f in as_completed(futures)]

    total_time = time.time() - start
    reads_per_sec = num_reads / total_time

    # Calculate statistics
    if latencies:
        avg_latency = statistics.mean(latencies)
        p50_latency = statistics.median(latencies)
        p99_latency = (
            sorted(latencies)[int(len(latencies) * 0.99)]
            if len(latencies) > 10
            else max(latencies)
        )
        max_latency = max(latencies)
    else:
        avg_latency = p50_latency = p99_latency = max_latency = 0

    print(f"\n  Results:")
    print(f"    Total time:     {total_time:.2f}s")
    print(f"    Throughput:     {reads_per_sec:.1f} reads/sec")
    print(f"    Avg latency:    {avg_latency:.1f}ms")
    print(f"    P50 latency:    {p50_latency:.1f}ms")
    print(f"    P99 latency:    {p99_latency:.1f}ms")
    print(f"    Max latency:    {max_latency:.1f}ms")

    # Cleanup
    router.close_all()

    return {
        "strategy": strategy_name,
        "insert_time": insert_time,
        "insert_rate": insert_rate,
        "throughput": reads_per_sec,
        "avg_latency": avg_latency,
        "p50_latency": p50_latency,
        "p99_latency": p99_latency,
        "max_latency": max_latency,
    }


def main():
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║         DATABASE SHARDING - LOAD TEST DEMO                   ║
║                                                              ║
║  This demo shows how sharding handles high traffic:         ║
║  • Insert stress: Bulk data insertion across shards          ║
║  • Read stress: Concurrent reads with multiple threads       ║
║  • Latency: Measure response times under load                ║
╚══════════════════════════════════════════════════════════════╝
    """
    )

    parser = argparse.ArgumentParser(description="Load Test Demo")
    parser.add_argument(
        "--strategy",
        choices=["no-sharding", "modulo", "hash", "consistent", "all"],
        default="all",
        help="Strategy to test",
    )
    parser.add_argument(
        "--users", type=int, default=1000, help="Number of users to insert"
    )
    parser.add_argument(
        "--reads", type=int, default=5000, help="Number of concurrent reads"
    )
    parser.add_argument(
        "--threads", type=int, default=20, help="Number of concurrent threads"
    )
    args = parser.parse_args()

    shards = create_test_shards(4)

    strategies = (
        ["no-sharding", "modulo", "hash", "consistent"]
        if args.strategy == "all"
        else [args.strategy]
    )

    results = []
    for strategy in strategies:
        result = run_load_test(strategy, shards, args.users, args.reads, args.threads)
        results.append(result)

    # Summary
    print(f"\n{'=' * 60}")
    print("  SUMMARY - Load Test Results")
    print(f"{'=' * 60}")
    print(
        f"\n  {'Strategy':<15} {'Throughput':>12} {'Avg Latency':>12} {'P99 Latency':>12}"
    )
    print(f"  {'-'*15} {'-'*12} {'-'*12} {'-'*12}")

    for r in results:
        print(
            f"  {r['strategy']:<15} {r['throughput']:>10.1f}/s {r['avg_latency']:>10.1f}ms {r['p99_latency']:>10.1f}ms"
        )

    # Compare sharding vs no-sharding
    if len(results) > 1:
        no_shard = next((r for r in results if r["strategy"] == "no-sharding"), None)
        sharded = [r for r in results if r["strategy"] != "no-sharding"]

        if no_shard and sharded:
            best = max(sharded, key=lambda x: x["throughput"])
            improvement = (
                (best["throughput"] - no_shard["throughput"]) / no_shard["throughput"]
            ) * 100

            print(f"\n  Sharding improves throughput by {improvement:.1f}%")
            print(
                f"  Best strategy: {best['strategy']} ({best['throughput']:.1f} reads/sec)"
            )


if __name__ == "__main__":
    main()
