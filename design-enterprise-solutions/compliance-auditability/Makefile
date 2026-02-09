# Makefile for Compliance & Auditability

.PHONY: help test bench test-all clean

help:
	@echo "Compliance & Auditability targets:"
	@echo "  test      - Run functional tests"
	@echo "  bench     - Run performance benchmarks"
	@echo "  test-all  - Run both functional and benchmark tests"
	@echo "  clean     - Remove local caches"

test:
	uv run pytest __test__

bench:
	uv run pytest benchmark-sdks/

test-all: test bench

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
