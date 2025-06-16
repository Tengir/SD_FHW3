"""
In-memory OrdersRepo + update_status.
"""
from __future__ import annotations
from typing import Any, Protocol, List

_ORDERS: list[dict[str, Any]] = []
_id_seq = 1

class OrdersRepo(Protocol):
    async def insert(self, user_id: int, amount: int) -> dict[str, Any]: ...
    async def select_by_user(self, user_id: int) -> List[dict[str, Any]]: ...
    async def select_one(self, user_id: int, order_id: int) -> dict[str, Any] | None: ...
    async def update_status(self, order_id: int, status: str) -> None: ...
    async def commit(self) -> None: ...

class InMemoryOrdersRepo:
    async def insert(self, user_id: int, amount: int) -> dict[str, Any]:
        global _id_seq
        order = {
            'id': _id_seq,
            'user_id': user_id,
            'amount': amount,
            'status': 'PENDING',
        }
        _id_seq += 1
        _ORDERS.append(order)
        return order

    async def select_by_user(self, user_id: int):
        return [o for o in _ORDERS if o['user_id'] == user_id]

    async def select_one(self, user_id: int, order_id: int):
        for o in _ORDERS:
            if o['id'] == order_id and o['user_id'] == user_id:
                return o
        return None

    async def update_status(self, order_id: int, status: str) -> None:
        for o in _ORDERS:
            if o['id'] == order_id:
                o['status'] = status

    async def commit(self):
        return None

_repo: OrdersRepo | None = None

def get_repo() -> OrdersRepo:
    global _repo
    if _repo is None:
        _repo = InMemoryOrdersRepo()
    return _repo
