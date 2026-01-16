# Build stage
FROM ghcr.io/astral-sh/uv:latest AS builder

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim-trixie

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser scr ./scr

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "scr.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
