import asyncio
from typing import Callable, Any

import pytest
from fastapi.testclient import TestClient

from orders.main import app as orders_app
from payments.main import app as payments_app

# —— Пользуемся глобальными in‑memory репами, нужно чистить данные перед каждым тестом.
from orders.repository import repository as orders_repo_mod
from payments.repository import repository as payments_repo_mod


@pytest.fixture(autouse=True)
def _reset_state():
    """Очищаем in‑memory‑хранилища до каждого теста."""
    orders_repo_mod._ORDERS.clear()  # type: ignore[attr-defined]
    orders_repo_mod._id_seq = 1  # type: ignore[attr-defined]
    payments_repo_mod._ACCOUNTS.clear()  # type: ignore[attr-defined]


@pytest.fixture(scope="session")
def event_loop():  # noqa: D401
    """FastAPI TestClient внутри pytest‑asyncio требует свой loop‑scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def orders_client() -> TestClient:  # noqa: D401
    with TestClient(orders_app) as c:
        yield c


@pytest.fixture()
def payments_client() -> TestClient:  # noqa: D401
    with TestClient(payments_app) as c:
        yield c


@pytest.fixture()
def publish_spy(monkeypatch: pytest.MonkeyPatch) -> list[
    tuple[str, dict]]:  # noqa: D401
    """Патчим fake_publish и собираем все вызовы для проверки."""
    calls: list[tuple[str, dict]] = []

    async def _fake(topic: str, msg: dict):  # noqa: D401
        calls.append((topic, msg))

    from shared import infra as _infra
    monkeypatch.setattr(_infra.mq, "fake_publish", _fake)
    return calls
