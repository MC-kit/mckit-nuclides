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
  poetry build
  poetry install  

# Clean build
rebuild: clean build

# Update dependencies
up:
  pre-commit autoupdate
  poetry update

# Aliases
alias t := test-all
