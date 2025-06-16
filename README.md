# Что внутри
API Gateway
Проксирует все HTTP-запросы к нужному сервису.
Никакой бизнес-логики, только маршрутизация.

Orders Service
Создание и просмотр заказов.
Пишет событие orders.created в RabbitMQ.

Payments Service
Счета пользователей: открыть, пополнить, узнать баланс.
Слушает orders.created, списывает деньги, шлёт payment.succeeded или payment.failed.

RabbitMQ
Один topic-exchange events.
Если брокер недоступен, сервисы автоматически падают в in-memory pub/sub (тестовый режим).

SQLite
Каждому сервису своя маленькая база: orders.db, payments.db.

Запуск в Docker
bash
Копировать
Редактировать

# Cобираем и стартуем всё сразу
docker compose up -d --build

# Логи в реальном времени
docker compose logs -f gateway orders payments rabbitmq
После старта:

Gateway доступен на http://localhost:8000

RabbitMQ-UI — http://localhost:15672 (guest/guest)

Мини-cheatsheet запросов:

# Создать счёт и пополнить
curl -X POST localhost:8000/payments/
curl -X POST localhost:8000/payments/topup -H "Content-Type: application/json" -d '{"amount":100}'

# Оформить заказ на 50
curl -X POST localhost:8000/orders/ -H "Content-Type: application/json" -d '{"amount":50}'

# Проверить статус
curl localhost:8000/orders/1
Локальная разработка без Docker

# Один раз установить зависимости (пример для orders):
cd orders
poetry install

# Запустить сервис
poetry run uvicorn orders.main:app --reload --port 8001
Запустите payments и gateway аналогично, RabbitMQ можно поднять отдельно:

docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Тесты
корень репо

pytest -q

Тесты используют in-memory брокер, поэтому RabbitMQ не обязателен.

# Postman

Лежит в каталоге