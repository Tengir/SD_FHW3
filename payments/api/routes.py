from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, NonNegativeInt

from payments.service.service import (
    create_account,
    get_balance,
    top_up,
)

router = APIRouter()


class TopUpIn(BaseModel):
    amount: NonNegativeInt


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(user_id: int = 1):  # noqa: D401
    return await create_account(user_id)


@router.post("/topup")
async def up(data: TopUpIn, user_id: int = 1):  # noqa: D401
    return await top_up(user_id, data.amount)


@router.get("/balance")
async def balance(user_id: int = 1):  # noqa: D401
    bal = await get_balance(user_id)
    if bal is None:
        raise HTTPException(status_code=404)
    return {'balance': bal}
