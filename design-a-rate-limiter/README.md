# Rate Limiter - Pluggable Architecture

A flexible, pluggable rate limiting system that supports multiple algorithms through a common interface. This architecture makes it easy to swap between different rate limiting strategies without changing server or client code.

Reference: https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter

## Architecture Overview

```
design-a-rate-limiter/
├── base.py                    # Abstract interfaces (RateLimiter, GlobalRateLimiter)
├── common_server.py           # Generic FastAPI server
├── common_client.py           # Generic test client
├── token-bucket/
│   ├── limiter.py            # Token Bucket implementation
│   └── run_server.py         # Token Bucket server
├── fixed-window-counter/
│   ├── limiter.py            # Fixed Window implementation
│   └── run_server.py         # Fixed Window server
└── ...
```

## Quick Start

```bash
# Start the token bucket server
poetry run python src/sys-design/design-a-rate-limiter/token-bucket/run_server.py

# In another terminal, run tests
poetry run python src/sys-design/design-a-rate-limiter/common_client.py
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed documentation.