# Makefile for Database Sharding Demo

.PHONY: help install up down restart logs clean run run-tradeoffs run-quant-metrics run-quant-metrics-md run-no-sharding run-modulo run-hash run-consistent prepare-load-test verify-data-mounts load-test load-test-no-sharding load-test-modulo load-test-hash load-test-consistent perf-profile-no-sharding perf-profile-modulo perf-profile-hash perf-profile-consistent perf-profile-all test

COMPOSE := docker-compose
PROFILE_DIR := profiles

# Default target
help:
	@echo "Database Sharding Demo - Available commands:"
	@echo ""
	@echo "  make install              - Install Python dependencies using uv"
	@echo "  make up                   - Start PostgreSQL shards with docker-compose"
	@echo "  make down                 - Stop and remove PostgreSQL containers"
	@echo "  make restart              - Restart PostgreSQL shards"
	@echo "  make logs                 - View logs from PostgreSQL containers"
	@echo "  make clean                - Remove Docker volumes and cache files"
	@echo ""
	@echo "  make run                  - Run distribution demo for all strategies"
	@echo "  make run-tradeoffs        - Run tradeoff scenarios section"
	@echo "  make run-quant-metrics    - Run raw quantitative metrics table"
	@echo "  make run-quant-metrics-md - Run quantitative metrics as markdown table"
	@echo "  make run-no-sharding      - Run demo for No Sharding strategy"
	@echo "  make run-modulo           - Run demo for Modulo strategy"
	@echo "  make run-hash             - Run demo for Hash-based strategy"
	@echo "  make run-consistent       - Run demo for Consistent Hashing strategy"
	@echo ""
	@echo "  make load-test            - Run load test for all strategies"
	@echo "  make prepare-load-test    - Reset volumes and bootstrap fresh PostgreSQL shards"
	@echo "  make verify-data-mounts   - Validate postgres data mounts in all running shards"
	@echo "  make load-test-no-sharding - Run load test for No Sharding"
	@echo "  make load-test-modulo     - Run load test for Modulo"
	@echo "  make load-test-hash       - Run load test for Hash-based"
	@echo "  make load-test-consistent - Run load test for Consistent Hashing"
	@echo "  make perf-profile-no-sharding - Run profile favoring no-sharding"
	@echo "  make perf-profile-modulo  - Run profile favoring modulo"
	@echo "  make perf-profile-hash    - Run profile favoring hash"
	@echo "  make perf-profile-consistent - Run profile favoring consistent hashing"
	@echo "  make perf-profile-from-config PROFILE=<name> - Run profile from profiles/<name>.env"
	@echo "  make perf-profile-all     - Run all 4 perf profiles sequentially"
	@echo ""
	@echo "  make test                 - Run tests"
	@echo ""

install:
	uv sync --dev --extra sharding

up:
	$(COMPOSE) up -d
	@echo "Waiting for PostgreSQL shards to be ready..."
	@sleep 5
	@echo "PostgreSQL shards are ready!"

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f

clean:
	$(COMPOSE) down -v
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

run:
	uv run --extra sharding python demo.py

run-tradeoffs:
	uv run --extra sharding python demo.py | sed -n '/Tradeoff Scenarios/,$$p'

run-quant-metrics-md:
	uv run --extra sharding python demo.py --report quant-md

run-no-sharding:
	uv run --extra sharding python demo.py --strategy no-sharding

run-modulo:
	uv run --extra sharding python demo.py --strategy modulo

run-hash:
	uv run --extra sharding python demo.py --strategy hash

run-consistent:
	uv run --extra sharding python demo.py --strategy consistent

# Load test commands - auto clean, setup, and run
prepare-load-test:
	@echo "Resetting shards to pristine state (remove prior volumes)..."
	-$(COMPOSE) down -v
	@echo "Bootstrapping fresh PostgreSQL shard containers..."
	$(COMPOSE) up -d
	@echo "Waiting for shard containers to pass health checks..."
	@for container in shard1 shard2 shard3 shard4; do \
		printf "  - waiting for %s" "$$container"; \
		for i in $$(seq 1 60); do \
			status=$$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}unknown{{end}}' "$$container" 2>/dev/null || true); \
			if [ "$$status" = "healthy" ]; then \
				echo " ... healthy"; \
				break; \
			fi; \
			if [ $$i -eq 60 ]; then \
				echo " ... failed (status=$$status)"; \
				exit 1; \
			fi; \
			printf "."; \
			sleep 1; \
		done; \
	done

verify-data-mounts:
	@echo "Validating postgres data mounts for shard containers..."
	@for container in shard1 shard2 shard3 shard4; do \
		mount_src=$$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Source}}{{end}}{{end}}' "$$container" 2>/dev/null || true); \
		if [ -z "$$mount_src" ]; then \
			echo "  - $$container: missing /var/lib/postgresql/data mount"; \
			exit 1; \
		fi; \
		echo "  - $$container: mounted $$mount_src"; \
	done

load-test: prepare-load-test verify-data-mounts
	uv run --extra sharding python load_test.py --strategy all

load-test-no-sharding: prepare-load-test verify-data-mounts
	uv run --extra sharding python load_test.py --strategy no-sharding

load-test-modulo: prepare-load-test verify-data-mounts
	uv run --extra sharding python load_test.py --strategy modulo

load-test-hash: prepare-load-test verify-data-mounts
	uv run --extra sharding python load_test.py --strategy hash

load-test-consistent: prepare-load-test verify-data-mounts
	uv run --extra sharding python load_test.py --strategy consistent

# Profiled performance runs: each profile is defined in profiles/*.env.
# Every profile starts from a pristine DB and validates data mounts first.
perf-profile-from-config: prepare-load-test verify-data-mounts
	@if [ -z "$(PROFILE)" ]; then \
		echo "Usage: make perf-profile-from-config PROFILE=<name>"; \
		echo "Example: make perf-profile-from-config PROFILE=hash"; \
		exit 1; \
	fi
	@profile_file="$(PROFILE_DIR)/$(PROFILE).env"; \
	if [ ! -f "$$profile_file" ]; then \
		echo "Profile config not found: $$profile_file"; \
		exit 1; \
	fi; \
	set -a; . "$$profile_file"; set +a; \
	echo "Running $$STRATEGY profile ($$DESCRIPTION)..."; \
	echo "Config: users=$$USERS reads=$$READS threads=$$THREADS"; \
	uv run --extra sharding python load_test.py --strategy "$$STRATEGY" --users "$$USERS" --reads "$$READS" --threads "$$THREADS"

perf-profile-no-sharding:
	$(MAKE) perf-profile-from-config PROFILE=no-sharding

perf-profile-modulo:
	$(MAKE) perf-profile-from-config PROFILE=modulo

perf-profile-hash:
	$(MAKE) perf-profile-from-config PROFILE=hash

perf-profile-consistent:
	$(MAKE) perf-profile-from-config PROFILE=consistent

perf-profile-all:
	$(MAKE) perf-profile-no-sharding
	$(MAKE) perf-profile-modulo
	$(MAKE) perf-profile-hash
	$(MAKE) perf-profile-consistent

test:
	uv run --extra sharding pytest -v
