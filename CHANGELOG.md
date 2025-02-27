# Changelog

All notable changes to the dbt-governance project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Project pull request (PR) template
- Basic usage example use cases to README
- Workflow for PRs to run tests via tox
- Bug report and feature request issue templates
- dependabot configuration for security and dependency alerts

### Changed

- Debug logging for rule evaluations to handle corner case

### Removed

- Black, isort and flake8 from the project config file and dev dependencies

## [0.1.0] - 2024-12-26

### Added

- Initial project setup, basic structure and features outline.
- Added basic CLI structure, behavior, and options for `dbt-governance` command.
- Initial support for `evaluate`, `list-rules`, and `validate-config` commands.
- Released initial model-only rules for `meta` and `tags` required values.
- Init `pyproject.toml` configurations, README, CONTRIBUTING, and CHANGELOG files.
- Added basic `tox` configuration for testing and linting.
- Configured project itself for code and security governance.
- Initial basic unit testing for project structures, not yet for rules or full coverage.

[unreleased]: https://github.com/jmbrooks/dbt-governance/compare/0.1.0...HEAD
[0.1.0]: https://github.com/jmbrooks/dbt-governance/releases/tag/0.1.0
