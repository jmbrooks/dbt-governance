# Contributing to dbt-governance

## Local development setup

Follow [these standard instructions](https://opensource.guide/how-to-contribute/#opening-a-pull-request) to get set up
for development. The general development pattern looks like this:

- Fork the dbt-governance repository on GitHub
- Clone the fork to your local machine
- Create a new local branch off `main` using the `feature/feature-name` branch naming convention
  - If you're fixing a bug, use branch naming `fix/bug-name` instead
- If you do not have `poetry` installed on your machine, follow installation instructions [here](https://python-poetry.org/docs/#installation)
- Create a Python virtual environment and install dependencies with `poetry install`
  - I'd recommend using [pyenv](https://github.com/pyenv/pyenv) to install all supported Python versions in order to run `tox` successfully on all supported versions

Once your local repository is set up, develop away on your feature! Double-check that you've included the following:

- [Tests](https://docs.pytest.org/en/latest/) added or updated `tests/` for any new code that you introduce
- [Type hints](https://docs.python.org/3/library/typing.html) for all input arguments and returned outputs
- [Docstrings](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) for all functions and classes, according to [Google Docstring Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- Running `tox` to ensure that all tests, linting, and formatting checks pass is your final step before submitting a PR

## Test requirements for submission

All pull requests (PRs) must pass the following checks:

- [`pytest`](https://docs.pytest.org/en/latest/) unit and integration tests
- [`ruff formatter`](https://docs.astral.sh/ruff/formatter/) to enforce [PEP 8](https://peps.python.org/pep-0008/) Python styles
- [`ruff linter`](https://docs.astral.sh/ruff/linter/) for robust checking and fixing of common Python errors and anti-patterns
- [`bandit`](https://github.com/PyCQA/bandit) for identifying common security issues in Python code

## Submitting a pull request

Once you've completed development, testing, docstrings, and type hinting, you're ready to submit a pull request. Create
a pull request from the feature branch in your fork to `main` in the main repository.

Reference any relevant issues in your PR. If your PR closes an issue, include it (e.g. "Closes #19") so the issue will
be auto-closed when the PR is merged.
