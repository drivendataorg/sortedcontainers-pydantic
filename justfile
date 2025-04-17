python := "3.13"

# Print this help documentation
help:
    just --list

# Sync requirements
sync:
    uv sync

# Run linting
lint:
    uv run ruff format --check
    uv run ruff check

# Run formatting
format:
    uv run ruff format
    uv run ruff check --fix

# Run static typechecking
typecheck:
    uv run --python {{python}} --no-dev --group typecheck --isolated \
        mypy sortedcontainers_pydantic tests/typechecks.py --install-types --non-interactive --strict

# Run the tests
test *args:
    uv run --python {{python}} --isolated --no-editable --no-dev --group tests --reinstall \
        python -I -m pytest {{args}}

# Run all tests with Python version matrix
test-all:
    for python in 3.9 3.10 3.11 3.12 3.13; do \
        just python=$python test; \
    done
