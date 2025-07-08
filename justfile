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
  uv version {{ARGS}} && git commit -m "bump: version $(uv version)" pyproject.toml


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
  uv update

# Aliases
alias t := test-all
alias c := check-all
