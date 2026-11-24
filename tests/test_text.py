import json
from pathlib import Path

import pytest

from app.metrics import edit_magnitude


CASES = json.loads((Path(__file__).parent / "fixtures" / "text_cases.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_text_fixture(case):
    metrics = edit_magnitude(case["draft"], case["final"], "text", **case["options"])
    actual = metrics.model_dump(mode="json")
    for field, expected in case["expected"].items():
        if isinstance(expected, float):
            assert actual[field] == pytest.approx(expected, abs=0.00005)
        else:
            assert actual[field] == expected


def test_invalid_text_input_is_rejected():
    with pytest.raises(TypeError):
        edit_magnitude({"text": "x"}, "x", "text")
