import asyncio

# —— Пользуемся глобальными in‑memory репами, нужно чистить данные перед каждым тестом.
from payments.repository import repository as payments_repo_mod


def test_payments_repo_basic():  # noqa: D401
    repo = payments_repo_mod.get_repo()

    # create account
    acc = asyncio.run(repo.create_account(99))
    assert acc["balance"] == 0

    # top up
    acc = asyncio.run(repo.top_up(99, 150))
    assert acc["balance"] == 150

    # balance lookup
    bal = asyncio.run(repo.get_balance(99))
    assert bal == 150
