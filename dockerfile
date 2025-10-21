# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ARG PROJECT_HOME=/insperion_api

EXPOSE 8000

RUN mkdir -p ${PROJECT_HOME}
WORKDIR ${PROJECT_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y gcc libpq-dev python3-dev

COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

ADD . ${PROJECT_HOME}/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

COPY .cicd/include/run-migrations.py /usr/local/bin/run-migrations.py
RUN chmod +x /usr/local/bin/run-migrations.py

CMD [ \
    "uv", \
    "run", \
    "--", \
    "uvicorn", \
    "insperion_api.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--reload" \
    ]

FROM builder AS api