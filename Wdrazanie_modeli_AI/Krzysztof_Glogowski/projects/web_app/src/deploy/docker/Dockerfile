FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN uv sync --locked --no-install-project --no-editable --group web-app --extra cpu

COPY ./projects/web_app/src/web_app ./web_app/
COPY ./projects/common/src/common ./common/

FROM python:3.12-slim-bookworm AS service

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder app/web_app web_app
COPY --from=builder app/common common
COPY --from=builder app/.venv .venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app/web_app

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]