from collections.abc import Awaitable, Callable
from typing import Protocol
import uuid


class ReviewSubmittedQueue(Protocol):
    async def enqueue(self, event_id: uuid.UUID) -> None: ...


class InProcessReviewQueue:
    """Small local queue adapter; production can bind this protocol to Redis."""

    def __init__(self, handler: Callable[[uuid.UUID], Awaitable[None]]) -> None:
        self._handler = handler

    async def enqueue(self, event_id: uuid.UUID) -> None:
        await self._handler(event_id)
