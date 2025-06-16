from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, NonNegativeInt

from orders.service.service import create_order, list_orders, get_order

router = APIRouter()


class OrderIn(BaseModel):
    amount: NonNegativeInt


@router.post("/", status_code=status.HTTP_201_CREATED)
async def place(order: OrderIn, user_id: int = 1):  # noqa: D401
    return await create_order(user_id, order.amount)


@router.get("/")
async def all_orders(user_id: int = 1):  # noqa: D401
    return await list_orders(user_id)


@router.get("/{order_id}")
async def by_id(order_id: int, user_id: int = 1):  # noqa: D401
    order = await get_order(user_id, order_id)
    if not order:
        raise HTTPException(status_code=404)
    return order
