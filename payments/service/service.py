"""
Payments бизнес-логика + handler для orders.created.
"""
from typing import Any
from payments.repository.repository import PaymentsRepo, get_repo, AccountNotFound, InsufficientFunds
import shared.infra.mq as mq


async def create_account(user_id: int) -> dict[str, Any]:
    return await get_repo().create_account(user_id)


async def get_balance(user_id: int) -> int | None:
    return await get_repo().get_balance(user_id)


async def top_up(user_id: int, amount: int) -> dict[str, Any]:
    return await get_repo().top_up(user_id, amount)


async def handle_order_created(message: dict[str, Any]) -> None:
    """
    При orders.created: списать баланс и опубликовать succeeded/failed.
    """
    order_id = message["order_id"]
    user_id  = message["user_id"]
    amount   = message["amount"]
    repo: PaymentsRepo = get_repo()

    # Гарантируем, что счёт есть
    try:
        await repo.create_account(user_id)
    except Exception:
        pass

    try:
        result = await repo.charge(user_id, amount)
        await mq.publish("payment.succeeded", {
            "order_id": order_id, "user_id": user_id, "balance": result["balance"],
        })
    except AccountNotFound:
        await mq.publish("payment.failed", {
            "order_id": order_id, "user_id": user_id, "reason": "no_account",
        })
    except InsufficientFunds:
        await mq.publish("payment.failed", {
            "order_id": order_id, "user_id": user_id, "reason": "insufficient_funds",
        })
