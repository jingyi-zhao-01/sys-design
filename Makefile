# Makefile for Enterprise Design Solutions Monorepo

.PHONY: help install test lint format clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install       - Install dependencies using uv"
	@echo "  test          - Run all tests in the workspace"
	@echo "  test-audit    - Run Compliance & Auditability tests"
	@echo "  test-iam      - Run Identity & Access Plane tests"
	@echo "  test-control  - Run Multi-Tenant Control Plane tests"
	@echo "  test-policy   - Run Policy & Governance Engine tests"
	@echo "  bench-audit   - Run Compliance & Auditability benchmarks"
	@echo "  lint          - Run ruff and mypy"
	@echo "  format        - Format code using ruff"
	@echo "  clean         - Remove cache files and build artifacts"

install:
	uv sync --all-extras --dev

test:
	uv run pytest

test-audit:
	uv run pytest design-enterprise-solutions/compliance-auditability/__test__

test-iam:
	@if [ -d "design-enterprise-solutions/identity-and-access-plane/__test__" ]; then \
		uv run pytest design-enterprise-solutions/identity-and-access-plane/__test__; \
	else \
		echo "No tests found for iam."; \
	fi

test-control:
	@if [ -d "design-enterprise-solutions/multi-tenant-control-plane/__test__" ]; then \
		uv run pytest design-enterprise-solutions/multi-tenant-control-plane/__test__; \
	else \
		echo "No tests found for control plane."; \
	fi

test-policy:
	@if [ -d "design-enterprise-solutions/policy-governance-engine/__test__" ]; then \
		uv run pytest design-enterprise-solutions/policy-governance-engine/__test__; \
	else \
		echo "No tests found for policy engine."; \
	fi

bench-audit:
	uv run pytest design-enterprise-solutions/compliance-auditability/benchmark-sdks/

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache .venv .coverage htmlcov
