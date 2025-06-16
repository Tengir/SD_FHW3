# Syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Сначала копируем только метаданные проекта
COPY orders/pyproject.toml orders/poetry.lock* /app/

# Устанавливаем poetry и зависимости (без создания venv)
RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# Копируем код самого сервиса и общий пакет
COPY orders/    /app/orders/
COPY shared/    /app/shared/

EXPOSE 8001

CMD ["uvicorn", "orders.main:app", "--host", "0.0.0.0", "--port", "8001"]
