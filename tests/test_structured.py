import json
from pathlib import Path

import pytest

from app.metrics import edit_magnitude


CASES = json.loads((Path(__file__).parent / "fixtures" / "structured_cases.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_structured_fixture(case):
    metrics = edit_magnitude(case["draft"], case["final"], "structured").model_dump(mode="json")
    expected = case["expected"]
    for field in ("field_edit_ratio", "changed_fields", "total_fields", "critical_edits"):
        value = expected[field]
        if isinstance(value, float):
            assert metrics[field] == pytest.approx(value, abs=0.00005)
        else:
            assert metrics[field] == value
    assert metrics["list_changes"] == expected["list_changes"]


def test_list_alignment_uses_configurable_primary_key():
    metrics = edit_magnitude(
        {"custom_items": [{"key": "a", "label": "旧"}]},
        {"custom_items": [{"key": "a", "label": "新"}]},
        "structured",
        list_fields={"custom_items"},
        primary_key="key",
    )
    assert metrics.list_changes["custom_items"].modified == 1


def test_duplicate_list_keys_are_rejected():
    with pytest.raises(ValueError, match="duplicate primary key"):
        edit_magnitude(
            {"todos": [{"id": "t1"}, {"id": "t1"}]},
            {"todos": []},
            "structured",
        )
