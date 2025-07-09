set dotenv-load := true

default:
  @just --list

test-ff *ARGS:
  pytest -vv -x {{ARGS}}

# test-cache-clear *ARGS:
#   pytest -vv --cache-clear {{ARGS}}

# test-fast *ARGS:
#   pytest -m "not slow" {{ARGS}}

test-all *ARGS:
  pytest {{ARGS}}

coverage:
  coverage run --parallel -m pytest

coverage-html: coverage
  coverage html

# Run pre-commit on all files
pre-commit:
  pre-commit run -a 


# Check style and test all
check-all: pre-commit test-all

bump *ARGS:
  #!/bin/bash
  uv version --bump {{ARGS}}
  git commit -m "bump: version $(uv version)" pyproject.toml uv.lock 

# Clean reproducible files
clean:
  #!/bin/bash
  to_clean=(
      ".benchmarks"
      ".cache"
      ".eggs"
      ".mypy_cache"
      ".nox"
      ".pytest_cache"
      ".ruff_cache"
      "__pycache__"
      "_skbuild"
      "build"
      "dist"
      "docs/_build"
      "htmlcov"
      "setup.py"
  )
  rm -fr ${to_clean[@]}


build:
  uv build

# Clean build
rebuild: clean build

install:
  uv pip install -e .  

# Update dependencies
up:
  pre-commit autoupdate
  uv self update

docs-build:
  uv run --no-dev --group docs sphinx-build docs/source docs/_build

docs:
  uv run --no-dev --group docs --group docs-auto sphinx-autobuild --open-browser docs/source docs/_build

ruff:
  ruff check --fix src tests
  ruff format src tests


# Aliases
alias t := test-all
alias c := check-all
