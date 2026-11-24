from collections.abc import Mapping, Sequence
from typing import Any

from .models import EditMetrics, ListChange

DEFAULT_LIST_FIELDS = frozenset({"payment_milestones", "benefits", "todos"})
DEFAULT_CRITICAL_FIELDS = frozenset(
    {"credit_code", "unified_social_credit_code"}
)


def _is_critical_key(key: str, configured: frozenset[str]) -> bool:
    lowered = key.casefold()
    return (
        lowered in configured
        or lowered.endswith("amount")
        or lowered.endswith("_cents")
    )


def _validate_list(value: Any, field_name: str, primary_key: str) -> dict[Any, Mapping[str, Any]]:
    if not isinstance(value, list):
        raise TypeError(f"configured list field {field_name!r} must contain a list")
    indexed: dict[Any, Mapping[str, Any]] = {}
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise TypeError(f"{field_name}[{index}] must be an object")
        if primary_key not in item:
            raise ValueError(f"{field_name}[{index}] is missing primary key {primary_key!r}")
        key = item[primary_key]
        try:
            duplicate = key in indexed
        except TypeError as exc:
            raise TypeError(f"{field_name}[{index}] has an unhashable primary key") from exc
        if duplicate:
            raise ValueError(f"{field_name} contains duplicate primary key {key!r}")
        indexed[key] = item
    return indexed


def _count_critical_changes(
    before: Any,
    after: Any,
    *,
    configured: frozenset[str],
    list_fields: frozenset[str],
    primary_key: str,
    parent_key: str | None = None,
) -> int:
    if before == after:
        return 0
    if parent_key is not None and _is_critical_key(parent_key, configured):
        return 1

    if isinstance(before, Mapping) or isinstance(after, Mapping):
        before_map = before if isinstance(before, Mapping) else {}
        after_map = after if isinstance(after, Mapping) else {}
        count = 0
        for key in before_map.keys() | after_map.keys():
            if not isinstance(key, str):
                continue
            old = before_map.get(key, _MISSING)
            new = after_map.get(key, _MISSING)
            if old == new:
                continue
            if _is_critical_key(key, configured):
                count += 1
            elif key in list_fields and (isinstance(old, list) or old is _MISSING) and (
                isinstance(new, list) or new is _MISSING
            ):
                old_items = _validate_list([] if old is _MISSING else old, key, primary_key)
                new_items = _validate_list([] if new is _MISSING else new, key, primary_key)
                for item_id in old_items.keys() | new_items.keys():
                    count += _count_critical_changes(
                        old_items.get(item_id, _MISSING),
                        new_items.get(item_id, _MISSING),
                        configured=configured,
                        list_fields=list_fields,
                        primary_key=primary_key,
                    )
            else:
                count += _count_critical_changes(
                    old,
                    new,
                    configured=configured,
                    list_fields=list_fields,
                    primary_key=primary_key,
                    parent_key=key,
                )
        return count

    if before is _MISSING or after is _MISSING:
        return 0
    return 0


_MISSING = object()


def calculate_structured_metrics(
    draft: Mapping[str, Any],
    final: Mapping[str, Any],
    *,
    list_fields: frozenset[str] = DEFAULT_LIST_FIELDS,
    primary_key: str = "id",
    critical_fields: frozenset[str] = DEFAULT_CRITICAL_FIELDS,
) -> EditMetrics:
    if not isinstance(draft, Mapping) or not isinstance(final, Mapping):
        raise TypeError("structured drafts and finals must be mappings")
    if not all(isinstance(key, str) for key in (*draft.keys(), *final.keys())):
        raise TypeError("structured field names must be strings")

    all_fields = draft.keys() | final.keys()
    list_change_results: dict[str, ListChange] = {}
    changed_fields = 0

    for field in all_fields:
        before = draft.get(field, _MISSING)
        after = final.get(field, _MISSING)
        if before == after:
            continue
        changed_fields += 1
        if field in list_fields:
            old_items = _validate_list([] if before is _MISSING else before, field, primary_key)
            new_items = _validate_list([] if after is _MISSING else after, field, primary_key)
            added = len(new_items.keys() - old_items.keys())
            removed = len(old_items.keys() - new_items.keys())
            modified = sum(
                old_items[item_id] != new_items[item_id]
                for item_id in old_items.keys() & new_items.keys()
            )
            list_change_results[field] = ListChange(
                added=added, removed=removed, modified=modified
            )

    total_fields = len(all_fields)
    ratio = changed_fields / total_fields if total_fields else 0.0
    critical_count = _count_critical_changes(
        draft,
        final,
        configured=critical_fields,
        list_fields=list_fields,
        primary_key=primary_key,
    )

    return EditMetrics(
        kind="structured",
        field_edit_ratio=ratio,
        changed_fields=changed_fields,
        total_fields=total_fields,
        list_changes=list_change_results,
        critical_edits=critical_count,
    )
