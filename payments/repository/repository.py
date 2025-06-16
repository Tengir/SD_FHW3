"""
Simplest in-memory repository + charge API.
"""
from __future__ import annotations
from typing import Protocol

# user_id -> balance
_ACCOUNTS: dict[int, int] = {}

class AccountNotFound(Exception):
    pass

class InsufficientFunds(Exception):
    pass

class PaymentsRepo(Protocol):
    async def create_account(self, user_id: int) -> dict: ...
    async def top_up(self, user_id: int, amount: int) -> dict: ...
    async def get_balance(self, user_id: int) -> int | None: ...
    async def charge(self, user_id: int, amount: int) -> dict: ...

class InMemoryPaymentsRepo:
    async def create_account(self, user_id: int):
        _ACCOUNTS.setdefault(user_id, 0)
        return {'user_id': user_id, 'balance': _ACCOUNTS[user_id]}

    async def top_up(self, user_id: int, amount: int):
        if user_id not in _ACCOUNTS:
            raise AccountNotFound("Account not found")
        _ACCOUNTS[user_id] += amount
        return {'balance': _ACCOUNTS[user_id]}

    async def get_balance(self, user_id: int):
        return _ACCOUNTS.get(user_id)

    async def charge(self, user_id: int, amount: int):
        if user_id not in _ACCOUNTS:
            raise AccountNotFound("Account not found")
        if _ACCOUNTS[user_id] < amount:
            raise InsufficientFunds("Not enough balance")
        _ACCOUNTS[user_id] -= amount
        return {'balance': _ACCOUNTS[user_id]}

_repo: PaymentsRepo | None = None

def get_repo() -> PaymentsRepo:
    global _repo
    if _repo is None:
        _repo = InMemoryPaymentsRepo()
    return _repo
