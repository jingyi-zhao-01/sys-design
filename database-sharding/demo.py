#!/usr/bin/env python3
"""
Interactive demo for database sharding strategies.
Demonstrates:
- Hash-based sharding
- Modulo-based partitioning
- Consistent hashing
- Rebalancing behavior
"""

import argparse
import random
import statistics
import time
from typing import Dict, List, Optional, Tuple
from strategies.base import Shard, ShardingStrategy
from strategies.modulo_sharding import ModuloSharding
from strategies.hash_sharding import HashSharding
from strategies.consistent_hashing import ConsistentHashing
from strategies.no_sharding import NoSharding


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


def generate_test_keys(count: int = 1000) -> List[str]:
    """Generate random test keys (simulating user IDs)."""
    return [f"user_{i:06d}" for i in range(count)]


def get_distribution_counts(
    strategy: ShardingStrategy, keys: List[str]
) -> Dict[int, int]:
    """Return per-shard key counts for a strategy."""
    distribution = {s.shard_id: 0 for s in strategy.get_all_shards()}
    for key in keys:
        shard = strategy.get_shard(key)
        distribution[shard.shard_id] += 1
    return distribution


def distribution_std_dev(distribution: Dict[int, int]) -> float:
    """Compute standard deviation for per-shard distribution counts."""
    counts = list(distribution.values())
    if not counts:
        return 0.0
    ideal = sum(counts) / len(counts)
    variance = sum((c - ideal) ** 2 for c in counts) / len(counts)
    return variance**0.5


def calculate_key_movement(
    strategy_class,
    old_shards: List[Shard],
    new_shards: List[Shard],
    keys: List[str],
    **strategy_kwargs,
) -> float:
    """Return percentage of keys that move when topology changes."""
    old_strategy = strategy_class(old_shards, **strategy_kwargs)
    new_strategy = strategy_class(new_shards, **strategy_kwargs)

    moved = 0
    for key in keys:
        if old_strategy.get_shard(key).shard_id != new_strategy.get_shard(key).shard_id:
            moved += 1
    return (moved / len(keys)) * 100 if keys else 0.0


def benchmark_lookup_ops_per_sec(
    strategy: ShardingStrategy, keys: List[str], rounds: int = 6
) -> float:
    """Microbenchmark for routing lookups (operations per second)."""
    start = time.perf_counter()
    for _ in range(rounds):
        for key in keys:
            strategy.get_shard(key)
    elapsed = time.perf_counter() - start
    total_ops = len(keys) * rounds
    return (total_ops / elapsed) if elapsed > 0 else 0.0


def normalize_higher_is_better(values: Dict[str, float]) -> Dict[str, float]:
    """Normalize a metric dictionary into 0-10 where higher is better."""
    metric_values = list(values.values())
    minimum = min(metric_values)
    maximum = max(metric_values)
    if maximum == minimum:
        return {k: 10.0 for k in values}
    return {k: ((v - minimum) / (maximum - minimum)) * 10.0 for k, v in values.items()}


def normalize_lower_is_better(values: Dict[str, float]) -> Dict[str, float]:
    """Normalize a metric dictionary into 0-10 where lower is better."""
    higher = normalize_higher_is_better(values)
    return {k: 10.0 - v for k, v in higher.items()}


def build_strategy_metrics(keys: List[str]) -> Dict[str, Dict[str, float]]:
    """Build comparable metrics for all four strategies from measured benchmarks."""
    shards_4 = create_test_shards(4)
    shards_5 = create_test_shards(5)
    shard_1 = create_test_shards(1)
    hot_keys = [f"hot_user_{i % 50:02d}" for i in range(len(keys))]

    strategy_defs = {
        "no-sharding": (NoSharding, {}),
        "modulo": (ModuloSharding, {}),
        "hash": (HashSharding, {}),
        "consistent": (ConsistentHashing, {"virtual_nodes": 100}),
    }

    raw_metrics: Dict[str, Dict[str, float]] = {}
    for name, (strategy_class, kwargs) in strategy_defs.items():
        strategy_4 = strategy_class(shards_4, **kwargs)
        strategy_5 = strategy_class(shards_5, **kwargs)
        strategy_1 = strategy_class(shard_1, **kwargs)

        distribution_uniform = get_distribution_counts(strategy_4, keys)
        distribution_hot = get_distribution_counts(strategy_4, hot_keys)

        uniform_std = distribution_std_dev(distribution_uniform)
        hot_std = distribution_std_dev(distribution_hot)

        moved_pct = calculate_key_movement(
            strategy_class, shards_4, shards_5, keys, **kwargs
        )

        lookup_ops_4 = benchmark_lookup_ops_per_sec(strategy_4, keys)
        lookup_ops_1 = benchmark_lookup_ops_per_sec(strategy_1, keys)

        util_4 = len(strategy_4.get_all_shards()) / len(shards_4)
        util_5 = len(strategy_5.get_all_shards()) / len(shards_5)

        # Penalize strategies that cannot use newly added shards.
        effective_moved_pct = moved_pct + (1.0 - util_5) * 100.0

        raw_metrics[name] = {
            "lookup_ops_4": lookup_ops_4,
            "lookup_ops_1": lookup_ops_1,
            "uniform_std": uniform_std,
            "hot_std": hot_std,
            "moved_pct": moved_pct,
            "effective_moved_pct": effective_moved_pct,
            "shard_utilization_4": util_4,
            "shard_utilization_5": util_5,
        }

    # Normalize benchmark metrics into comparable 0-10 scores.
    lookup_4_score = normalize_higher_is_better(
        {k: v["lookup_ops_4"] for k, v in raw_metrics.items()}
    )
    lookup_1_score = normalize_higher_is_better(
        {k: v["lookup_ops_1"] for k, v in raw_metrics.items()}
    )
    uniform_balance_score = normalize_lower_is_better(
        {k: v["uniform_std"] for k, v in raw_metrics.items()}
    )
    hot_balance_score = normalize_lower_is_better(
        {k: v["hot_std"] for k, v in raw_metrics.items()}
    )
    rebalance_score = normalize_lower_is_better(
        {k: v["effective_moved_pct"] for k, v in raw_metrics.items()}
    )
    scale_utilization_score = normalize_higher_is_better(
        {k: v["shard_utilization_4"] for k, v in raw_metrics.items()}
    )

    # For scenarios that require sharding, normalize only among sharded strategies.
    sharded_names = ["modulo", "hash", "consistent"]
    lookup_4_sharded_score = normalize_higher_is_better(
        {k: raw_metrics[k]["lookup_ops_4"] for k in sharded_names}
    )
    uniform_balance_sharded_score = normalize_lower_is_better(
        {k: raw_metrics[k]["uniform_std"] for k in sharded_names}
    )
    hot_balance_sharded_score = normalize_lower_is_better(
        {k: raw_metrics[k]["hot_std"] for k in sharded_names}
    )
    rebalance_sharded_score = normalize_lower_is_better(
        {k: raw_metrics[k]["effective_moved_pct"] for k in sharded_names}
    )

    metrics: Dict[str, Dict[str, float]] = {}
    for name, measured in raw_metrics.items():
        metrics[name] = {
            **measured,
            "lookup_speed_4_score": lookup_4_score[name],
            "lookup_speed_1_score": lookup_1_score[name],
            "uniform_balance_score": uniform_balance_score[name],
            "hot_balance_score": hot_balance_score[name],
            "rebalance_score": rebalance_score[name],
            "scale_utilization_score": scale_utilization_score[name],
            "lookup_speed_sharded_score": lookup_4_sharded_score.get(name, 0.0),
            "uniform_balance_sharded_score": uniform_balance_sharded_score.get(
                name, 0.0
            ),
            "hot_balance_sharded_score": hot_balance_sharded_score.get(name, 0.0),
            "rebalance_sharded_score": rebalance_sharded_score.get(name, 0.0),
        }

    return metrics


def score_scenario(
    metrics: Dict[str, Dict[str, float]],
    weights: Dict[str, float],
    eligible_strategies: Optional[List[str]] = None,
) -> List[Tuple[str, float]]:
    """Weighted score across metrics; returns sorted results."""
    results: List[Tuple[str, float]] = []
    for strategy_name, strategy_metrics in metrics.items():
        if eligible_strategies and strategy_name not in eligible_strategies:
            continue
        total = 0.0
        for metric_name, weight in weights.items():
            total += strategy_metrics.get(metric_name, 0.0) * weight
        results.append((strategy_name, total))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def demo_tradeoff_scenarios() -> None:
    """Show four situations where each strategy stands out."""
    print(f"\n{'=' * 60}")
    print("  Tradeoff Scenarios: Which Strategy Wins When?")
    print(f"{'=' * 60}")

    keys = generate_test_keys(5000)
    metrics = build_strategy_metrics(keys)

    print("\n  Perf test inputs:")
    print("    - lookup benchmark: get_shard() on 5,000 keys x 6 rounds")
    print("    - balance benchmark: uniform keys + hot-key workload")
    print("    - scaling benchmark: key movement when adding shard (4 -> 5)")

    scenarios = [
        {
            "name": "1) Early-stage MVP, one DB can handle traffic",
            "winner_should_be": "no-sharding",
            "eligible_strategies": ["no-sharding", "modulo", "hash", "consistent"],
            "weights": {
                "lookup_speed_1_score": 0.70,
                "lookup_speed_4_score": 0.30,
            },
            "reason": "For small scale, winner is fastest in routing microbenchmarks.",
        },
        {
            "name": "2) Stable cluster size, need simplest horizontal partitioning",
            "winner_should_be": "modulo",
            "eligible_strategies": ["modulo", "hash", "consistent"],
            "weights": {
                "scale_utilization_score": 0.25,
                "lookup_speed_sharded_score": 0.60,
                "uniform_balance_sharded_score": 0.15,
            },
            "reason": "Shard count is stable, so prioritize steady-state throughput + balanced spread.",
        },
        {
            "name": "3) Read-heavy workload with hot keys (avoid shard hotspots)",
            "winner_should_be": "hash",
            "eligible_strategies": ["modulo", "hash", "consistent"],
            "weights": {
                "hot_balance_sharded_score": 0.35,
                "lookup_speed_sharded_score": 0.50,
                "scale_utilization_score": 0.15,
            },
            "reason": "Winner keeps hottest workload more evenly spread while staying fast.",
        },
        {
            "name": "4) Elastic infrastructure with frequent scale in/out",
            "winner_should_be": "consistent",
            "eligible_strategies": ["modulo", "hash", "consistent"],
            "weights": {
                "rebalance_sharded_score": 0.65,
                "scale_utilization_score": 0.15,
                "uniform_balance_sharded_score": 0.10,
                "lookup_speed_sharded_score": 0.10,
            },
            "reason": "Winner minimizes effective data movement while still using new capacity.",
        },
    ]

    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"  Context: {scenario['reason']}")
        print(f"  Candidates: {', '.join(scenario['eligible_strategies'])}")

        ranking = score_scenario(
            metrics,
            scenario["weights"],
            eligible_strategies=scenario["eligible_strategies"],
        )
        expected = scenario["winner_should_be"]

        for strategy_name, score in ranking:
            moved = metrics[strategy_name]["moved_pct"]
            lookup_ops = metrics[strategy_name]["lookup_ops_4"]
            print(
                f"    - {strategy_name:11s} score={score:5.2f} | lookup={lookup_ops:9.0f} ops/s | moved={moved:5.1f}%"
            )

        winner = ranking[0][0]
        status = "OK" if winner == expected else f"NOTE: expected {expected}"
        print(f"  Winner: {winner} ({status})")


def visualize_distribution(strategy: ShardingStrategy, keys: List[str], title: str):
    """Visualize how keys are distributed across shards."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")

    # Count distribution
    distribution = {s.shard_id: 0 for s in strategy.get_all_shards()}
    for key in keys:
        shard = strategy.get_shard(key)
        distribution[shard.shard_id] += 1

    # Calculate statistics
    counts = list(distribution.values())
    total = sum(counts)
    ideal = total // len(counts)

    print(f"\nShard Distribution:")
    print("-" * 40)

    max_count = max(counts) if counts else 1
    bar_width = 40

    for shard_id, count in sorted(distribution.items()):
        bar_length = int((count / max_count) * bar_width)
        bar = "█" * bar_length
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  Shard {shard_id}: {bar:<{bar_width}} {count:4d} ({percentage:5.1f}%)")

    # Calculate variance
    if counts:
        variance = sum((c - ideal) ** 2 for c in counts) / len(counts)
        std_dev = variance**0.5
        print(f"\n  Ideal per shard: {ideal}")
        print(f"  Std deviation: {std_dev:.1f}")
        print(f"  Distribution quality: {'GOOD' if std_dev < 50 else 'POOR'}")


def demo_routing_determinism(strategy: ShardingStrategy):
    """Show that the same key always routes to the same shard."""
    print(f"\n{'=' * 60}")
    print(f"  Routing Determinism Test")
    print(f"{'=' * 60}")

    test_keys = ["user_123", "user_456", "user_789", "alice", "bob"]

    print("\n  Same key → Same shard (multiple lookups):")
    for key in test_keys:
        results = [strategy.get_shard(key).shard_id for _ in range(5)]
        unique = set(results)
        status = "✓ PASS" if len(unique) == 1 else "✗ FAIL"
        print(f"    {key:15s} → Shard {results[0]} ({status})")


def demo_rebalancing(strategy_class, original_keys: List[str]):
    """Show how different strategies handle rebalancing."""
    print(f"\n{'=' * 60}")
    print(f"  Rebalancing Comparison")
    print(f"{'=' * 60}")

    original_shards = create_test_shards(4)
    new_shards = create_test_shards(5)  # Add one more shard

    # Test with original shards
    original_strategy = strategy_class(original_shards)
    original_distribution = {}
    for key in original_keys:
        shard = original_strategy.get_shard(key)
        original_distribution[key] = shard.shard_id

    # Test with new shards
    new_strategy = strategy_class(new_shards)
    new_distribution = {}
    for key in original_keys:
        shard = new_strategy.get_shard(key)
        new_distribution[key] = shard.shard_id

    # Count how many keys moved
    moved = sum(
        1 for k in original_keys if original_distribution[k] != new_distribution[k]
    )
    percentage = (moved / len(original_keys)) * 100

    print(f"\n  Adding 1 shard (4 → 5):")
    print(f"    Keys that moved: {moved}/{len(original_keys)} ({percentage:.1f}%)")

    if percentage < 50:
        print(f"    ✓ Good for dynamic scaling")
    else:
        print(f"    ✗ Requires significant data migration")


def demo_consistent_hashing_virtual_nodes():
    """Demonstrate the effect of virtual nodes."""
    print(f"\n{'=' * 60}")
    print(f"  Virtual Nodes Effect (Consistent Hashing)")
    print(f"{'=' * 60}")

    keys = generate_test_keys(1000)
    shards = create_test_shards(4)

    for vn in [1, 10, 50, 100]:
        strategy = ConsistentHashing(shards, virtual_nodes=vn)

        distribution = {s.shard_id: 0 for s in shards}
        for key in keys:
            shard = strategy.get_shard(key)
            distribution[shard.shard_id] += 1

        counts = list(distribution.values())
        ideal = len(keys) // len(shards)
        variance = sum((c - ideal) ** 2 for c in counts) / len(counts)
        std_dev = variance**0.5

        print(f"\n  Virtual nodes = {vn}:")
        print(f"    Distribution: {counts}")
        print(f"    Std deviation: {std_dev:.1f}")


def print_quantitative_metrics_table(markdown: bool = False) -> None:
    """Print raw quantitative metrics for each strategy (no score/winner logic)."""
    if not markdown:
        print(f"\n{'=' * 60}")
        print("  Quantitative Metrics (Raw Data)")
        print(f"{'=' * 60}")

    random.seed(42)

    keys = generate_test_keys(10000)
    shards_4 = create_test_shards(4)
    shards_5 = create_test_shards(5)

    strategy_defs = {
        "no-sharding": (NoSharding, {}),
        "modulo": (ModuloSharding, {}),
        "hash": (HashSharding, {}),
        "consistent": (ConsistentHashing, {"virtual_nodes": 100}),
    }

    # 80/20-style hot workload over 100 logical users.
    hot_population = [f"hot_user_{i:03d}" for i in range(100)]
    weights = [1.0 / ((i + 1) ** 1.2) for i in range(100)]
    hot_requests = random.choices(hot_population, weights=weights, k=20000)

    # Cross-shard query workload: 1000 queries, each touches 20 keys.
    batch_queries = [random.sample(keys, 20) for _ in range(1000)]

    columns = [
        "strategy",
        "throughput_qps",
        "lat_p50_ms",
        "lat_p95_ms",
        "lat_p99_ms",
        "data_balance_cv_pct",
        "load_balance_cv_pct",
        "rebalancing_moved_pct",
        "storage_scale_factor_4_to_5",
        "cross_shard_query_ratio_pct",
        "routing_cost_avg_us",
        "failure_blast_radius_pct",
        "op_complexity_routing_metadata_entries",
        "op_complexity_active_shards_4",
        "op_complexity_active_shards_5",
    ]

    if markdown:
        print(
            "| Strategy | Throughput (QPS) | Latency P50 (ms) | Latency P95 (ms) | Latency P99 (ms) | "
            "Data Distribution Balance (CV %) | Load Distribution Balance (CV %) | "
            "Rebalancing Cost: Data Moved (%) | Storage Capacity Scaling (4->5) | "
            "Cross-shard Query Ratio (%) | Routing Cost Avg (us) | Failure Blast Radius (%) | "
            "Operational Complexity: Routing Metadata Entries | "
            "Operational Complexity: Active Shards (4) | Operational Complexity: Active Shards (5) |"
        )
        print(
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
        )
    else:
        print("\n" + ",".join(columns))

    for name, (strategy_class, kwargs) in strategy_defs.items():
        strategy_4 = strategy_class(shards_4, **kwargs)
        strategy_5 = strategy_class(shards_5, **kwargs)

        # 1) Throughput (QPS) + 2) Latency (P50/P95/P99) from routing benchmark.
        lat_ms: List[float] = []
        start = time.perf_counter()
        total_calls = 0
        for _ in range(5):
            for key in keys:
                t0 = time.perf_counter()
                strategy_4.get_shard(key)
                lat_ms.append((time.perf_counter() - t0) * 1000.0)
                total_calls += 1
        elapsed = time.perf_counter() - start
        throughput_qps = total_calls / elapsed

        lat_sorted = sorted(lat_ms)

        def percentile(values: List[float], p: float) -> float:
            index = int((len(values) - 1) * p)
            return values[index]

        lat_p50_ms = percentile(lat_sorted, 0.50)
        lat_p95_ms = percentile(lat_sorted, 0.95)
        lat_p99_ms = percentile(lat_sorted, 0.99)
        routing_cost_avg_us = (sum(lat_ms) / len(lat_ms)) * 1000.0

        # 3) Data distribution balance: coefficient of variation (%) on uniform keys.
        uniform_counts = {sid: 0 for sid in [1, 2, 3, 4]}
        for key in keys:
            sid = strategy_4.get_shard(key).shard_id
            uniform_counts[sid] += 1
        uniform_values = list(uniform_counts.values())
        uniform_mean = sum(uniform_values) / len(uniform_values)
        uniform_std = statistics.pstdev(uniform_values)
        data_balance_cv_pct = (
            (uniform_std / uniform_mean * 100.0) if uniform_mean else 0.0
        )

        # 4) Load distribution balance: coefficient of variation (%) on hot workload.
        hot_counts = {sid: 0 for sid in [1, 2, 3, 4]}
        for key in hot_requests:
            sid = strategy_4.get_shard(key).shard_id
            hot_counts[sid] += 1
        hot_values = list(hot_counts.values())
        hot_mean = sum(hot_values) / len(hot_values)
        hot_std = statistics.pstdev(hot_values)
        load_balance_cv_pct = (hot_std / hot_mean * 100.0) if hot_mean else 0.0

        # 5) Rebalancing cost (data moved).
        rebalancing_moved_pct = calculate_key_movement(
            strategy_class, shards_4, shards_5, keys, **kwargs
        )

        # 6) Storage capacity scaling from 4 to 5 shards.
        active_shards_4 = len(strategy_4.get_all_shards())
        active_shards_5 = len(strategy_5.get_all_shards())
        storage_scale_factor = (
            (active_shards_5 / active_shards_4) if active_shards_4 else 0.0
        )

        # 7) Cross-shard query ratio: % batch queries touching >1 shard.
        multi_shard = 0
        for query_keys in batch_queries:
            touched = {strategy_4.get_shard(key).shard_id for key in query_keys}
            if len(touched) > 1:
                multi_shard += 1
        cross_shard_query_ratio_pct = (multi_shard / len(batch_queries)) * 100.0

        # 9) Failure blast radius: % keys impacted when shard 1 fails.
        impacted = 0
        for key in keys:
            if strategy_4.get_shard(key).shard_id == 1:
                impacted += 1
        failure_blast_radius_pct = (impacted / len(keys)) * 100.0

        # 10) Operational complexity: routing metadata size + active shard counts.
        if name == "consistent":
            routing_metadata_entries = len(strategy_4._ring)
        else:
            routing_metadata_entries = len(strategy_4.get_all_shards())

        if markdown:
            print(
                f"| {name} | {throughput_qps:.2f} | {lat_p50_ms:.6f} | {lat_p95_ms:.6f} | {lat_p99_ms:.6f} | "
                f"{data_balance_cv_pct:.2f} | {load_balance_cv_pct:.2f} | {rebalancing_moved_pct:.2f} | "
                f"{storage_scale_factor:.2f} | {cross_shard_query_ratio_pct:.2f} | {routing_cost_avg_us:.2f} | "
                f"{failure_blast_radius_pct:.2f} | {routing_metadata_entries} | {active_shards_4} | {active_shards_5} |"
            )
        else:
            row = [
                name,
                f"{throughput_qps:.2f}",
                f"{lat_p50_ms:.6f}",
                f"{lat_p95_ms:.6f}",
                f"{lat_p99_ms:.6f}",
                f"{data_balance_cv_pct:.2f}",
                f"{load_balance_cv_pct:.2f}",
                f"{rebalancing_moved_pct:.2f}",
                f"{storage_scale_factor:.2f}",
                f"{cross_shard_query_ratio_pct:.2f}",
                f"{routing_cost_avg_us:.2f}",
                f"{failure_blast_radius_pct:.2f}",
                str(routing_metadata_entries),
                str(active_shards_4),
                str(active_shards_5),
            ]
            print(",".join(row))


def main(strategy_name: Optional[str] = None, report: Optional[str] = None):
    if report == "quant":
        print_quantitative_metrics_table()
        return
    if report == "quant-md":
        print_quantitative_metrics_table(markdown=True)
        return

    print(
        """
╔══════════════════════════════════════════════════════════════╗
║         DATABASE SHARDING STRATEGIES DEMO                    ║
║                                                              ║
║  This demo shows how different sharding strategies:         ║
║  • Distribute data across multiple database nodes            ║
║  • Route requests to the correct shard                       ║
║  • Handle adding/removing shards (rebalancing)               ║
╚══════════════════════════════════════════════════════════════╝
    """
    )

    # Generate test keys
    keys = generate_test_keys(1000)
    shards = create_test_shards(4)

    # Map strategy names to classes
    strategy_map = {
        "no-sharding": (NoSharding, "No Sharding (Baseline)"),
        "modulo": (ModuloSharding, "Modulo-Based Sharding"),
        "hash": (HashSharding, "Hash-Based Sharding"),
        "consistent": (ConsistentHashing, "Consistent Hashing"),
    }

    # Determine which strategies to run
    if strategy_name:
        if strategy_name not in strategy_map:
            print(f"Unknown strategy: {strategy_name}")
            print(f"Available strategies: {', '.join(strategy_map.keys())}")
            return
        strategies = [strategy_map[strategy_name]]
    else:
        strategies = [
            (NoSharding, "No Sharding (Baseline)"),
            (ModuloSharding, "Modulo-Based Sharding"),
            (HashSharding, "Hash-Based Sharding"),
            (ConsistentHashing, "Consistent Hashing"),
        ]

    for strategy_class, name in strategies:
        strategy = strategy_class(shards)
        visualize_distribution(strategy, keys, name)
        demo_routing_determinism(strategy)

    # Only show rebalancing comparison for all strategies when no specific strategy selected
    if not strategy_name:
        # Rebalancing comparison
        print("\n\n")
        demo_rebalancing(ModuloSharding, keys)
        demo_rebalancing(ConsistentHashing, keys)

        # Virtual nodes demo
        demo_consistent_hashing_virtual_nodes()

        # Scenario-driven tradeoff analysis
        demo_tradeoff_scenarios()

    print(f"\n{'=' * 60}")
    print("  Summary")
    print(f"{'=' * 60}")
    print(
        """
  ┌─────────────────────┬────────────┬────────────┬────────────┬────────────┐
  │ Strategy            │ Lookup     │ Rebalancing│ Distribution│ Scaling    │
  ├─────────────────────┼────────────┼────────────┼────────────┼────────────┤
  │ No Sharding         │ O(1)       │ N/A        │ Single node│ None       │
  │ Modulo              │ O(1)       │ ALL data   │ Good       │ Poor       │
  │ Hash-based          │ O(1)       │ ALL data   │ Good       │ Poor       │
  │ Consistent Hashing  │ O(log N)   │ Minimal    │ Good+VN    │ Excellent  │
  └─────────────────────┴────────────┴────────────┴────────────┴────────────┘
    """
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database Sharding Demo")
    parser.add_argument(
        "--strategy",
        choices=["no-sharding", "modulo", "hash", "consistent"],
        help="Run demo for a specific strategy",
    )
    parser.add_argument(
        "--report",
        choices=["quant", "quant-md"],
        help="Print quantitative metrics report as CSV table",
    )
    args = parser.parse_args()
    main(args.strategy, args.report)
