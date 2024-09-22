FROM python:3.10-alpine AS build-stage

# Set environment variables
ENV POETRY_VERSION=1.8.3
ENV PYTHONUNBUFFERED=1

RUN pip install poetry=="${POETRY_VERSION}"
ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app

# Minimal copy to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/
RUN poetry -v install --no-dev --no-interaction --no-ansi --no-cache

COPY . /app
ENTRYPOINT ["poetry", "run", "aeternum"]

# Override the entrypoint to start a shell if no command is provided
CMD ["--help"]
