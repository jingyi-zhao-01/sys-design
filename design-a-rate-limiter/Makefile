# Makefile for Rate Limiter Designs

.PHONY: help test clean

help:
	@echo "Rate Limiter targets:"
	@echo "  test      - Run all rate limiter tests"
	@echo "  clean     - Remove local caches"

test:
	uv run pytest .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
