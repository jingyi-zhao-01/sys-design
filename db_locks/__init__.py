"""
Database Locking System Design

Implements various database locking mechanisms and concurrency control.

Key components:
- Optimistic locking with versioning
- Pessimistic locking with row-level locks
- Distributed locks with Redis
- Deadlock detection and prevention
"""

from .optimistic_lock import OptimisticLockManager
from .pessimistic_lock import PessimisticLockManager
from .distributed_lock import DistributedLockManager

__all__ = ["OptimisticLockManager", "PessimisticLockManager", "DistributedLockManager"]
