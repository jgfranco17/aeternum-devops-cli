# Behave Tests

This directory contains the feature files and step definitions for testing the CLI tool
using [Behave](https://behave.readthedocs.io/en/stable/).

## Structure

- **`testcases/`**: Contains the feature files written in Gherkin syntax, which define the
  BDD test scenarios
- **`steps/`**: Python files with step implementations that define how each Gherkin step should be executed

## Running Tests

To run the Behave tests, execute the following command:

```bash
poetry run behave tests/features
```

This helps validate the behavior of the project from a user requirement perspective.
