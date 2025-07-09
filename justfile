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

typeguard *ARGS:
  @uv run --no-dev --group test --group typeguard pytest -vv --emoji --typeguard-packages=src {{ARGS}}

xdoctest *ARGS:
  @uv run --no-dev --group test --group xdoctest python -m xdoctest --silent --style google -c all src tools {{ARGS}}


coverage:
  uv run --no-dev --group coverage coverage run --parallel -m pytest
  uv run --no-dev --group coverage coverage combine
  uv run --no-dev --group coverage coverage report

coverage-html: coverage
  uv run --no-dev --group coverage coverage html

# Run pre-commit on all files
pre-commit:
  uv run --no-dev --group pre-commit pre-commit run -a 

# Run mypy
mypy:
  uv run --no-dev --group mypy mypy src docs/source/conf.py


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
