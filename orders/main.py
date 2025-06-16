import os
import uvicorn
from fastapi import FastAPI

from shared.infra.db import init_db
import shared.infra.mq as mq
from orders.api.routes import router as orders_router
from orders.service.service import handle_payment_succeeded, handle_payment_failed

app = FastAPI(title="Orders Service", version="0.1.0")

# Эндпоинты и на корне, и под /orders/ (для тестов)
app.include_router(orders_router)
app.include_router(orders_router, prefix="/orders")

RABBIT = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

@app.on_event("startup")
async def startup() -> None:
    await init_db("sqlite+aiosqlite:///orders.db")
    # Инициализируем MQ (fallback на память, если не доступен)
    await mq.init_mq(RABBIT, "orders")
    # Подписываемся **динамически**
    mq.subscribe("payment.succeeded", handle_payment_succeeded)
    mq.subscribe("payment.failed",    handle_payment_failed)

@app.on_event("shutdown")
async def shutdown() -> None:
    await mq.close_mq()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
