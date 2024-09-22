# Aeternum

Aeternum is a powerful and user-friendly command-line interface (CLI) tool designed to help you
define and run build step automations for CI/CD in your projects.

In future iterations, a companion API will be available and integrated into this tool.

## Project Code Coverage

![Coverage](https://img.shields.io/badge/coverage-100.00-green?style=for-the-badge)

## Development Setup

### Preqrequisites

Before getting started on development for this project, install the following on your local machine:

- [Python 3.10](https://www.python.org/downloads/) or above

Additional installs; optional, for developer convenience

- [Just](https://github.com/casey/just) command runner
- [Direnv](https://direnv.net/docs/installation.html)

Aeternum can be installed using Poetry. Ensure you have Poetry installed on your system.

1. Clone the repository

   ```shell
   git clone https://github.com/jgfranco17/aeternum-devops-cli.git
   cd aeternum
   ```

2. Install dependencies

   ```shell
   poetry install
   ```

3. Use a virtual environment for development

   ```shell
   poetry install
   ```

There is also a Docker implementation available.

```shell
docker build -t aeternum .
docker run --rm aeternum --version
```

## Usage

You can use Aeternum directly through the command line.

```shell
aeternum --help
```
