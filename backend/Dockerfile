FROM python:3.12-slim
WORKDIR /app

# build deps for Poetry and asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash build-essential python3-dev libpq-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# install dependencies
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# copy source
COPY app /app/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
