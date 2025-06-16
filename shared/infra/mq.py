"""
Мини-шина сообщений (in-memory + RabbitMQ).

Экпортируем:
    publish(topic, message)
    subscribe(topic, handler)
    fake_publish, get_fake_calls, clear_fake_calls
    init_mq(amqp_url, service_name)
    close_mq()

Логика
------
● По умолчанию — чисто in-memory: удобно для pytest.
● init_mq(...)  → пробуем подключиться к RabbitMQ, если удачно —
  заменяем publish/subscribe на реальные; если нет — тихий fallback.
● close_mq()    → закрывает RobustConnection, если был.
"""

from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol

# ------------------------------------------------------------------ in-memory layer
_fake_calls: List[tuple[str, dict[str, Any]]] = []
_subs: Dict[str, List[Callable[[dict[str, Any]], Awaitable[None]]]] = {}

async def fake_publish(topic: str, message: dict[str, Any]) -> None:
    _fake_calls.append((topic, message))
    print(f"[MQ FAKE] {topic=} {message=}")

def get_fake_calls() -> List[tuple[str, dict[str, Any]]]:
    return list(_fake_calls)

def clear_fake_calls() -> None:
    _fake_calls.clear()

async def _mem_publish(topic: str, message: dict[str, Any]) -> None:
    await fake_publish(topic, message)
    for h in _subs.get(topic, []):
        with suppress(Exception):
            await h(message)

def _mem_subscribe(topic: str, handler: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
    _subs.setdefault(topic, []).append(handler)

# ------------------------------------------------------------------ exported api (default = memory)
publish:   Callable[[str, dict[str, Any]], Awaitable[None]] = _mem_publish
subscribe: Callable[[str, Callable[[dict[str, Any]], Awaitable[None]]], None] = _mem_subscribe

# ------------------------------------------------------------------ RabbitMQ init (optional)
_conn = None          # RobustConnection | None
_channel = None       # RobustChannel    | None
_exchange = None      # RobustExchange   | None

async def init_mq(amqp_url: str, service: str) -> None:
    """
    Пытаемся перейти на RabbitMQ, иначе остаёмся в памяти.
    Можно смело вызывать в тестах – падать не будет.
    """
    global publish, subscribe, _conn, _channel, _exchange

    try:
        import aio_pika
        from aio_pika import ExchangeType, Message, IncomingMessage

        _conn = await aio_pika.connect_robust(amqp_url)
        _channel = await _conn.channel()
        _exchange = await _channel.declare_exchange("events", ExchangeType.TOPIC, durable=True)

        async def _rb_publish(topic: str, message: dict[str, Any]) -> None:
            body = json.dumps(message).encode()
            msg = Message(body)
            await _exchange.publish(msg, routing_key=topic)

        def _rb_subscribe(topic: str, handler: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
            queue_name = f"{service}.{topic}"

            async def _consume() -> None:
                queue = await _channel.declare_queue(queue_name, durable=True)
                await queue.bind(_exchange, routing_key=topic)

                async def _on(msg: IncomingMessage) -> None:
                    async with msg.process(ignore_processed=True):
                        payload = json.loads(msg.body.decode())
                        await handler(payload)

                await queue.consume(_on)

            asyncio.create_task(_consume())

        publish = _rb_publish      # type: ignore
        subscribe = _rb_subscribe  # type: ignore
        print("[MQ] RabbitMQ backend enabled")

    except Exception as e:  # noqa: BLE001
        # остаёмся на in-memory
        print(f"[MQ] RabbitMQ init failed → fallback to memory ({e})")

async def close_mq() -> None:
    """Закрыть RabbitMQ соединение, если было."""
    global _conn
    if _conn and not _conn.is_closed:
        await _conn.close()
