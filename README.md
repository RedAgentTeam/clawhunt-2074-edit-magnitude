# Edit Magnitude

Python 3.11+ module for calculating text and structured edit metrics and writing those metrics back to a review event.

## Requirements

- Python 3.11 or later
- PostgreSQL 16 for the production database
- Redis for the production queue adapter

The test suite uses SQLite in memory through `aiosqlite`. All fixtures are fictional and local. Runtime code does not make network requests or read credentials.

## Install

```bash
cd edit_magnitude
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

## Run tests

```bash
pytest -q
```

The performance test prints the maximum of five calculations for a deterministic 5,000-character pair and checks that it is no more than 0.2 seconds.

## Calculate metrics

```python
from app.metrics import edit_magnitude

text_metrics = edit_magnitude("初稿内容。", "修改后的内容。", "text")
structured_metrics = edit_magnitude(
    {"amount_cents": 12000}, {"amount_cents": 15000}, "structured"
)
```

`ignore_whitespace=True` applies only to text calculations. It removes Unicode whitespace and Unicode punctuation before calculating the character-level Levenshtein ratio. Sentence matching uses the original text, splits on Chinese and Western sentence punctuation (`。！？!?；;`) and line breaks, and compares sentence multisets.

For structured calculations, each top-level key is a field. The denominator is the union of keys in both versions. The default list fields are `payment_milestones`, `benefits`, and `todos`; records align by `id`. Callers can pass `list_fields`, `primary_key`, and `critical_fields` to adapt these rules. Amount keys ending in `amount` or `_cents`, plus `credit_code` and `unified_social_credit_code`, count as critical fields. Each changed critical field counts once, including fields within aligned list records.

## Event writeback and integration points

`ReviewEvent` is the SQLAlchemy 2 event model with the shared UUID, organization, site, audit, and soft-delete fields. After persisting a `review_submitted` event, enqueue its ID and invoke `handle_review_submitted(event_id, async_session)`. The handler loads the event, skips calculation for `status == "rejected"`, computes metrics for other statuses, writes the JSON result to `metrics`, and commits the session.

`ReviewSubmittedQueue` in `app/events/stubs.py` is the queue boundary. The included in-process adapter supports local wiring. In production, connect the protocol to the service's Redis queue and provide an `AsyncSession` backed by PostgreSQL 16. The interface is intentionally isolated from any external event bus or Redis client.

## Output fields

Text results include `edit_ratio`, `grade`, retained/deleted/added sentence metrics. Structured results include `field_edit_ratio`, `changed_fields`, `total_fields`, per-list added/removed/modified counts, and `critical_edits`. Fields that do not apply to a calculation are `null`.
