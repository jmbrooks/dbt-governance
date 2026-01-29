# Contributing to dbt-governance

## Prerequisites

1. Install `uv`

    [uv](https://github.com/astral-sh/uv) is the recommended package manager for this project
    (it replaces pip, venv, and pip-tools). It’s fast, reproducible, and automatically manages virtual environments.

    Install `uv` with one of its standalone installers:

    ```bash
    # On macOS and Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    ```bash
    # On Windows
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2. Install Proper Python Version

    `uv` requires an existing Python interpreter. If you don’t have Python 3.12 installed, you can either:
    - Use your system default (`run uv venv .venv --seed`), or
    - Install Python 3.12 using `pyenv` (or similar tool), for example (on Mac):

    ```bash
    brew update
    brew install pyenv
    pyenv install 3.12.11
    pyenv local 3.12.11
    ```

## Environment Setup

1. Create Virtual Environment

    ```bash
    uv venv .venv --seed --python 3.12
    ```

2. Sync Virtual Environment (Install Dependencies)

    ```bash
    uv sync
    uv run pre-commit install
    ```

3. Validate Environment

    ```bash
    uv run ruff check .
    uv run pytest
    uv run semantic_search
    ```

    You should see ruff properly confirm no linting errors, tests run, and successfully see the semantic search CLI help output, respectively.

## Development Commands

If you're on MacOS or Linux, the `Makefile` provides handy aliases for local development:

```bash
make setup    - create .venv, sync deps, install hooks
make install  - uv sync deps
make dev      - install + run pre-commit on all files
make lint     - ruff check + format check
make fmt      - ruff fix + format
make test     - pytest
make cov      - pytest with coverage
make lock     - write lockfile without upgrading (CI reproducibility)
make upgrade  - upgrade deps in lockfile, then sync
make env      - show tool versions
make clean    - remove caches/build artifacts
```

## Submitting a pull request

Once you've completed development, testing, docstrings, and type hinting, you're ready to submit a pull request. Create
a pull request from the feature branch in your fork to `main` in the main repository.

Reference any relevant issues in your PR. If your PR closes an issue, include it (e.g. "Closes #19") so the issue will
be auto-closed when the PR is merged.
