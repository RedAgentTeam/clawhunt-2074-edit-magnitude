from collections.abc import Mapping
from typing import Any

from .models import EditMetrics, Kind
from .structured import calculate_structured_metrics
from .text import calculate_text_metrics


def edit_magnitude(
    draft: str | Mapping[str, Any],
    final: str | Mapping[str, Any],
    kind: str | Kind,
    *,
    ignore_whitespace: bool = False,
    list_fields: set[str] | frozenset[str] | None = None,
    primary_key: str = "id",
    critical_fields: set[str] | frozenset[str] | None = None,
) -> EditMetrics:
    try:
        selected_kind = Kind(kind)
    except ValueError as exc:
        raise ValueError("kind must be 'text' or 'structured'") from exc

    if selected_kind is Kind.TEXT:
        if list_fields is not None or critical_fields is not None:
            raise ValueError("structured options cannot be used for text metrics")
        return calculate_text_metrics(
            draft, final, ignore_whitespace=ignore_whitespace  # type: ignore[arg-type]
        )

    if ignore_whitespace:
        raise ValueError("ignore_whitespace applies only to text metrics")
    from .structured import DEFAULT_CRITICAL_FIELDS, DEFAULT_LIST_FIELDS

    return calculate_structured_metrics(
        draft,  # type: ignore[arg-type]
        final,  # type: ignore[arg-type]
        list_fields=frozenset(list_fields) if list_fields is not None else DEFAULT_LIST_FIELDS,
        primary_key=primary_key,
        critical_fields=(
            frozenset(critical_fields)
            if critical_fields is not None
            else DEFAULT_CRITICAL_FIELDS
        ),
    )
