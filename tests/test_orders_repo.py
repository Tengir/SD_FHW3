import asyncio

# —— Пользуемся глобальными in‑memory репами, нужно чистить данные перед каждым тестом.
from orders.repository import repository as orders_repo_mod


def test_orders_repo_basic():  # noqa: D401
    repo = orders_repo_mod.get_repo()
    order = asyncio.run(repo.insert(user_id=42, amount=200))

    assert order["id"] == 1
    assert order["status"] == "PENDING"

    selected = asyncio.run(repo.select_one(42, 1))
    assert selected == order

    by_user = asyncio.run(repo.select_by_user(42))
    assert by_user == [order]
