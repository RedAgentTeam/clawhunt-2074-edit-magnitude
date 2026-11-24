import json
from pathlib import Path


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_fixture_set_has_24_fictional_cases():
    text_cases = json.loads((FIXTURE_DIR / "text_cases.json").read_text())
    structured_cases = json.loads((FIXTURE_DIR / "structured_cases.json").read_text())
    rejected_cases = json.loads((FIXTURE_DIR / "rejected_cases.json").read_text())
    assert (len(text_cases), len(structured_cases), len(rejected_cases)) == (14, 8, 2)
    assert len(text_cases) + len(structured_cases) + len(rejected_cases) == 24
