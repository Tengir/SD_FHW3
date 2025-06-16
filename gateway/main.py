# gateway/main.py

import os
from fastapi import FastAPI, Request, Response, status
import httpx

app = FastAPI(title="API-Gateway", version="0.1.0")

# Берём из окружения, либо используем имена сервисов из docker-compose
ORDER_SVC   = os.getenv("ORDERS_SERVICE_URL",   "http://orders:8001")
PAYMENT_SVC = os.getenv("PAYMENTS_SERVICE_URL", "http://payments:8002")

SERVICE_MAP = {
    "orders":   ORDER_SVC,
    "payments": PAYMENT_SVC,
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request) -> Response:
    target = SERVICE_MAP.get(service)
    print(f"DEBUG: {request.method} {target}/{path}")
    if not target:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            request.method,
            f"{target}/{path}",
            headers=request.headers.raw,
            content=await request.body(),
        )
    return Response(status_code=resp.status_code, content=resp.content, headers=resp.headers)
