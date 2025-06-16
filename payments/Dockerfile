# Syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

COPY payments/pyproject.toml payments/poetry.lock* /app/

RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

COPY payments/  /app/payments/
COPY shared/    /app/shared/

EXPOSE 8002

CMD ["uvicorn", "payments.main:app", "--host", "0.0.0.0", "--port", "8002"]
