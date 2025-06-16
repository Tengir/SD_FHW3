# Syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

COPY gateway/pyproject.toml gateway/poetry.lock* /app/

RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

COPY gateway/   /app/gateway/

EXPOSE 8000

CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
