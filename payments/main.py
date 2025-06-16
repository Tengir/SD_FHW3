import os
import uvicorn
from fastapi import FastAPI

from shared.infra.db import init_db
import shared.infra.mq as mq
from payments.api.routes import router as payments_router
from payments.service.service import handle_order_created

app = FastAPI(title="Payments Service", version="0.1.0")

# Эндпоинты для тестов и для Gateway
app.include_router(payments_router, prefix="/payments")
app.include_router(payments_router)

RABBIT = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

@app.on_event("startup")
async def startup() -> None:
    await init_db("sqlite+aiosqlite:///payments.db")
    await mq.init_mq(RABBIT, "payments")
    mq.subscribe("orders.created", handle_order_created)

@app.on_event("shutdown")
async def shutdown() -> None:
    await mq.close_mq()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
