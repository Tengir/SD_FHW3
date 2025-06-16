"""
Order бизнес-логика + публикация events.
"""
from typing import Any
from orders.repository.repository import OrdersRepo, get_repo
import shared.infra.mq as mq


async def create_order(user_id: int, amount: int) -> dict[str, Any]:
    """
    Создаёт заказ, коммитит и публикует событие orders.created.
    """
    repo: OrdersRepo = get_repo()
    order = await repo.insert(user_id=user_id, amount=amount)
    await repo.commit()
    # Динамический вызов, чтобы учесть возможный RabbitMQ backend
    await mq.publish(
        "orders.created",
        {"order_id": order["id"], "user_id": user_id, "amount": amount},
    )
    return order


async def list_orders(user_id: int) -> list[dict[str, Any]]:
    """Вернуть все заказы пользователя."""
    return await get_repo().select_by_user(user_id)


async def get_order(user_id: int, order_id: int) -> dict[str, Any] | None:
    """Вернуть один заказ."""
    return await get_repo().select_one(user_id, order_id)


async def handle_payment_succeeded(message: dict[str, Any]) -> None:
    """Обновить статус заказа в FINISHED."""
    repo: OrdersRepo = get_repo()
    await repo.update_status(message["order_id"], "FINISHED")
    await repo.commit()


async def handle_payment_failed(message: dict[str, Any]) -> None:
    """Обновить статус заказа в CANCELLED."""
    repo: OrdersRepo = get_repo()
    await repo.update_status(message["order_id"], "CANCELLED")
    await repo.commit()
