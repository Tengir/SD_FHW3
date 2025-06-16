import asyncio

from payments.service import service as payments_svc


def test_account_flow_service():  # noqa: D401
    acc = asyncio.run(payments_svc.create_account(10))
    assert acc["balance"] == 0

    acc = asyncio.run(payments_svc.top_up(10, 80))
    assert acc["balance"] == 80

    bal = asyncio.run(payments_svc.get_balance(10))
    assert bal == 80