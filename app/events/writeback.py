import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.metrics import edit_magnitude

from .models import ReviewEvent


async def handle_review_submitted(
    event_id: uuid.UUID, session: AsyncSession
) -> dict[str, object] | None:
    result = await session.execute(
        select(ReviewEvent).where(
            ReviewEvent.id == event_id,
            ReviewEvent.deleted_at.is_(None),
        )
    )
    event = result.scalar_one_or_none()
    if event is None or event.status == "rejected":
        return None

    metrics = edit_magnitude(event.draft, event.final, event.kind)
    payload = metrics.model_dump(mode="json")
    event.metrics = payload
    await session.commit()
    return payload
