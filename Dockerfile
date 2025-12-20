# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies required for building wheels and debugging
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --upgrade pip && pip install uv

# Copy project requirements
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies (respects uv.lock)
RUN uv sync --frozen --no-dev --no-editable

# Ensure the virtual environment is on PATH for every shell/user
ENV PATH="/app/.venv/bin:${PATH}"

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application (override in docker-compose if needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]