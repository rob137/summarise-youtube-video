# YouTube Transcript Extractor - Development Commands

.PHONY: help install install-dev test test-verbose test-coverage lint format clean

help:  ## Show this help message
	@echo "YouTube Transcript Extractor - Development Commands"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in development mode
	pip install -e .

install-dev:  ## Install with development dependencies
	pip install -e ".[dev]"

test:  ## Run the test suite
	pytest

test-verbose:  ## Run tests with verbose output
	pytest -v

test-coverage:  ## Run tests with coverage report
	pytest --cov=yt_transcript --cov-report=html --cov-report=term

test-regression:  ## Run only regression tests
	pytest tests/test_regression.py -v

test-cli:  ## Run only CLI tests
	pytest tests/test_cli.py -v

test-standalone:  ## Run only standalone script tests
	pytest tests/test_standalone_script.py -v

lint:  ## Run linting checks (if you want to add flake8/black later)
	@echo "Linting not configured yet. Consider adding flake8 or ruff."

format:  ## Format code (if you want to add black later)
	@echo "Formatting not configured yet. Consider adding black."

clean:  ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

check:  ## Run all checks (tests + any future linting)
	$(MAKE) test

verify:  ## Verify installation works
	yt-trans --help
	./yt-transcript dQw4w9WgXcQ || echo "Expected failure - this is just a connectivity test"

# Development workflow shortcuts
dev-setup: install-dev  ## Set up development environment
	@echo "✅ Development environment ready!"
	@echo "Run 'make test' to run the test suite"
	@echo "Run 'make help' to see all available commands"

ci: test  ## Run CI checks (currently just tests)
	@echo "✅ CI checks passed!"
