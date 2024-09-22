# Aeternum - Justfile utility

# Print list of available recipe (this)
default:
    @just --list --unsorted

# Run poetry install in all submodules
install:
    poetry install

# Run the CLI tool with Poetry
aeternum *ARGS:
    @poetry run aeternum {{ ARGS }}

# Build Docker image
build-docker:
    docker build -t aeternum .

# Run CLI through Docker
run-docker:
    docker run --rm -e GITHUB_API_TOKEN="${GITHUB_API_TOKEN}" -e GITHUB_USERNAME="${GITHUB_USERNAME}" aeternum --version

# Run pytest via poetry
pytest *ARGS:
    poetry run pytest {{ ARGS }}

# Run test coverage
coverage:
    poetry run coverage run --source=aeternum --omit="*/__*.py,*/test_*.py" -m pytest
    poetry run coverage report -m

get-project-coverage:
    poetry run coverage xml --omit="*/__*.py,*/test_*.py"
