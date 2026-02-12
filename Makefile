.PHONY: install test lint format type-check security clean build publish docs

# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest
BLACK = $(PYTHON) -m black
ISORT = $(PYTHON) -m isort
FLAKE8 = $(PYTHON) -m flake8
MYPY = $(PYTHON) -m mypy
BANDIT = $(PYTHON) -m bandit
SAFETY = $(PYTHON) -m safety

# Install dependencies
install:
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]
	$(PIP) install pre-commit
	pre-commit install

# Run tests
TEST_ARGS = -v --cov=microagent --cov-report=term-missing --cov-report=xml
TEST_PATH = tests/
test:
	$(PYTEST) $(TEST_ARGS) $(TEST_PATH)

test-cov:
	$(PYTEST) --cov=microagent --cov-report=html $(TEST_PATH)

# Linting and formatting
lint:
	$(FLAKE8 microagent tests
	$(MYPY) microagent tests

format:
	$(BLACK) microagent tests
	$(ISORT) microagent tests

format-check:
	$(BLACK) --check microagent tests
	$(ISORT) --check-only microagent tests

# Type checking
type-check:
	$(MYPY) microagent tests

# Security checks
security:
	$(BANDIT) -r microagent -x tests
	$(SAFETY) check --full-report

# Clean up
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/ build/ dist/ *.egg-info/ .eggs/

# Build package
build:
	$(PYTHON) -m build

# Publish to PyPI (requires TWINE_USERNAME and TWINE_PASSWORD environment variables)
publish: clean build
	twine upload dist/*

# Build documentation
docs:
	cd docs && make html

# Run all checks
check: format-check lint type-check security test

# Run pre-commit on all files
pre-commit-all:
	pre-commit run --all-files

# Update dependencies
update-deps:
	$(PIP) install --upgrade -e .[dev]
	pre-commit autoupdate

# Help
default: help
help:
	@echo "Available commands:"
	@echo "  install         - Install development dependencies"
	@echo "  test            - Run tests with coverage"
	@echo "  test-cov        - Generate HTML coverage report"
	@echo "  lint            - Run linters"
	@echo "  format          - Format code with black and isort"
	@echo "  format-check    - Check code formatting"
	@echo "  type-check      - Run type checking"
	@echo "  security        - Run security checks"
	@echo "  clean           - Remove build and cache files"
	@echo "  build           - Build package"
	@echo "  publish         - Publish to PyPI"
	@echo "  docs            - Build documentation"
	@echo "  check           - Run all checks (format, lint, type, security, test)"
	@echo "  pre-commit-all  - Run pre-commit on all files"
	@echo "  update-deps     - Update development dependencies"
	@echo "  help            - Show this help message"
