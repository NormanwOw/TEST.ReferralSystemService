FROM ghcr.io/astral-sh/uv:python3.13-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv venv && uv sync --frozen --no-cache

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/usr/local/lib/python3.10"