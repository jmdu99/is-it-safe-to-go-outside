# syntax=docker/dockerfile:1

# Builder stage: installs build dependencies and Python packages via Poetry
FROM python:3.12-slim AS builder
WORKDIR /app

# Install system packages required to build some Python wheels (e.g. asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
     build-essential \
     libpq-dev \
     libssl-dev \
     && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions and install dependencies
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && \
     poetry config virtualenvs.create false && \
     poetry install --no-root --no-interaction --no-ansi

# copy source
COPY . .

# Runtime stage: slim image containing only runtime dependencies and the application
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install only the system libraries needed at runtime. We avoid build tools here to keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends \
     libpq5 \
     libssl3 \
     ca-certificates \
     && rm -rf /var/lib/apt/lists/*

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application source code
COPY app /app/app

# Expose the FastAPI port
EXPOSE 8000

# Ensure the Python output is unbuffered so logs are flushed immediately
ENV PYTHONUNBUFFERED=1

# Default command to run the API. We explicitly use the array form of CMD so Docker doesn't invoke a shell.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
