import uuid
import json
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.events.models import Base, ReviewEvent
from app.events.writeback import handle_review_submitted

REJECTED_CASES = json.loads(
    (Path(__file__).parent / "fixtures" / "rejected_cases.json").read_text()
)


@pytest.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


async def add_event(factory, *, status, kind, draft, final):
    event = ReviewEvent(
        id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        site_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        status=status,
        kind=kind,
        draft=draft,
        final=final,
    )
    async with factory() as session:
        session.add(event)
        await session.commit()
        return event.id


@pytest.mark.parametrize("case", REJECTED_CASES, ids=lambda case: case["name"])
async def test_rejected_draft_keeps_metrics_empty(session_factory, monkeypatch, case):
    import app.events.writeback as writeback

    def unexpected_calculation(*args, **kwargs):
        raise AssertionError("rejected event must not be calculated")

    monkeypatch.setattr(writeback, "edit_magnitude", unexpected_calculation)
    event_id = await add_event(
        session_factory,
        status=case["status"],
        kind=case["kind"],
        draft=case["draft"],
        final=case["final"],
    )
    async with session_factory() as session:
        assert await handle_review_submitted(event_id, session) is None
        result = await session.execute(select(ReviewEvent).where(ReviewEvent.id == event_id))
        event = result.scalar_one()
        assert event.metrics == case["expected_metrics"]


async def test_submitted_event_metrics_are_written_back(session_factory):
    event_id = await add_event(
        session_factory,
        status="submitted",
        kind="structured",
        draft={"amount_cents": 100},
        final={"amount_cents": 150},
    )
    async with session_factory() as session:
        payload = await handle_review_submitted(event_id, session)
        assert payload["critical_edits"] == 1
        result = await session.execute(select(ReviewEvent).where(ReviewEvent.id == event_id))
        assert result.scalar_one().metrics["critical_edits"] == 1
