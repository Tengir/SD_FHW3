import asyncio

from orders.service import service as orders_svc


def test_create_order_publishes_event(publish_spy):  # noqa: D401
    order = asyncio.run(orders_svc.create_order(user_id=1, amount=300))

    assert order["amount"] == 300
    assert publish_spy == [("orders.created", {"order_id": order["id"], "user_id": 1, "amount": 300})]


def test_list_and_get_orders():  # noqa: D401
    asyncio.run(orders_svc.create_order(5, 50))
    orders = asyncio.run(orders_svc.list_orders(5))
    assert len(orders) == 1

    got = asyncio.run(orders_svc.get_order(5, orders[0]["id"]))
    assert got == orders[0]