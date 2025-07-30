# syntax=docker/dockerfile:1

########################################################
# Builder stage: install build dependencies and app    #
########################################################
FROM python:3.12-slim AS builder
WORKDIR /app

# 1) Install system packages needed to compile native wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
     build-essential \
     libpq-dev \
     libssl-dev \
     && rm -rf /var/lib/apt/lists/*

# 2) Copy dependency definitions and install via Poetry
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# 3) Copy entire application source (including app/, storage/, tests, etc.)
COPY . /app

########################################################
# Runtime stage: slim image with only runtime deps     #
########################################################
FROM python:3.12-slim AS runtime
WORKDIR /app

# 4) Install only the system libraries needed at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
     libpq5 \
     libssl3 \
     ca-certificates \
     && rm -rf /var/lib/apt/lists/*

# 5) Copy Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 6) Copy all application code (app/, storage/, etc.) from builder
COPY --from=builder /app /app

# 7) Expose the FastAPI port and ensure unbuffered Python output
EXPOSE 8000
ENV PYTHONUNBUFFERED=1

# 8) Default command to run the API using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
