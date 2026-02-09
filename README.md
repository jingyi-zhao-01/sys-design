# System Design Practice

This directory contains practical implementations of common system design problems and patterns.

## Structure

Each system design problem is organized into its own package with clear separation of concerns:

### 1. URL Shortener (`url_shortener/`)
Implementation of a URL shortening service similar to bit.ly or TinyURL.

**Key Concepts:**
- Base62 encoding for compact URLs
- Hash collision handling
- Database schema design
- Scalability considerations

**Files:**
- `shortener.py` - Core URL shortening service
- `encoder.py` - Base62 encoding/decoding utilities

**Practice Topics:**
- Unique ID generation
- Hash functions
- Database indexing
- API design

---

### 2. Cache Systems (`cache/`)
Implementation of various caching strategies.

**Key Concepts:**
- Eviction policies (LRU, LFU, TTL)
- Memory management
- Performance optimization
- Cache invalidation

**Files:**
- `lru_cache.py` - Least Recently Used cache
- `lfu_cache.py` - Least Frequently Used cache
- `ttl_cache.py` - Time To Live cache

**Practice Topics:**
- Data structures (doubly linked list, hash map)
- Algorithm complexity
- Memory bounds
- Distributed caching

---

### 3. Database Locks (`db_locks/`)
Implementation of database locking mechanisms and concurrency control.

**Key Concepts:**
- Optimistic vs Pessimistic locking
- Deadlock prevention
- Distributed locks
- Transaction isolation

**Files:**
- `optimistic_lock.py` - Version-based optimistic locking
- `pessimistic_lock.py` - Explicit row-level locking
- `distributed_lock.py` - Redis-based distributed locks

**Practice Topics:**
- Concurrency control
- Race conditions
- Consistency guarantees
- CAP theorem

---

## Getting Started

1. **Choose a problem** - Start with any package that interests you
2. **Read the module docstrings** - Understand the requirements and design
3. **Implement the TODOs** - Fill in the placeholder methods
4. **Write tests** - Create test files to verify your implementation
5. **Optimize** - Analyze time/space complexity and optimize

## Testing Your Implementation

Create test files in a `tests/` subdirectory for each package:

```bash
src/sysdesign/url_shortener/tests/
src/sysdesign/cache/tests/
src/sysdesign/db_locks/tests/
```

Example test structure:
```python
import pytest
from src.sysdesign.cache import LRUCache

def test_lru_cache_basic():
    cache = LRUCache(capacity=2)
    cache.put(1, "one")
    cache.put(2, "two")
    assert cache.get(1) == "one"
    cache.put(3, "three")  # Evicts key 2
    assert cache.get(2) is None
```

## Interview Preparation

For each system design:
1. Understand the **requirements** and **scale**
2. Design the **high-level architecture**
3. Deep dive into **key components**
4. Discuss **trade-offs** and alternatives
5. Consider **scalability** and **reliability**

## Additional Topics to Add

Future system design problems to implement:
- Rate Limiter (token bucket, sliding window)
- Message Queue (pub/sub, queue management)
- Consistent Hashing (distributed systems)
- Load Balancer (round robin, least connections)
- Notification System (push, email, SMS)
- Search Autocomplete (trie, ranking)
- Web Crawler (BFS, politeness, deduplication)
