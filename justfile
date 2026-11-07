# Keep in sync with just-version in .github/workflows/*.yml
set minimum-version := '1.55.0'

python := shell("cat .python-version")

# Print this help documentation
help:
    just --list

# Sync dev environment dependencies
sync:
    uv sync

# Run linting (passes through args)
lint *args:
    uv run -- ruff format --check {{args}}
    uv run -- ruff check {{args}}

# Run formatting (passes through args)
format *args:
    uv run -- ruff format {{args}}
    uv run -- ruff check --fix {{args}}

# Audit GitHub Actions workflows with zizmor (passes through args)
zizmor *args:
    uvx --exclude-newer "7 days" zizmor .github/ {{args}}

# Run static typechecking (passes through args)
[arg("python", long)]
typecheck python=python *args:
    uv run --python={{python}} --isolated --no-dev --group typecheck -- \
        mypy --python-version={{python}} --install-types --non-interactive --strict \
        src/sortedcontainers_pydantic tests/typechecks.py {{args}}

# Run tests (passes through args)
[arg("python", long)]
test python=python *args:
    uv run --python={{python}} --isolated --no-editable --no-dev --group tests --reinstall -- \
        python -I -m pytest {{args}}

# Run all tests with Python version matrix
test-all:
    for python in 3.10 3.11 3.12 3.13 3.14 3.15; do \
        just test --python=$python; \
    done
