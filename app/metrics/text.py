import unicodedata
from collections import Counter

from rapidfuzz.distance import Levenshtein

from .models import EditMetrics, Grade

_SENTENCE_SEPARATORS = frozenset("。！？!?;；\n\r")


def _normalize_for_ratio(value: str) -> str:
    return "".join(
        char
        for char in value
        if not char.isspace() and not unicodedata.category(char).startswith("P")
    )


def _sentences(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    for char in value:
        if char in _SENTENCE_SEPARATORS:
            sentence = "".join(current).strip()
            if sentence:
                parts.append(sentence)
            current.clear()
        else:
            current.append(char)
    sentence = "".join(current).strip()
    if sentence:
        parts.append(sentence)
    return parts


def calculate_text_metrics(
    draft: str, final: str, *, ignore_whitespace: bool = False
) -> EditMetrics:
    if not isinstance(draft, str) or not isinstance(final, str):
        raise TypeError("text drafts and finals must be strings")

    compared_draft = _normalize_for_ratio(draft) if ignore_whitespace else draft
    compared_final = _normalize_for_ratio(final) if ignore_whitespace else final
    denominator = max(len(compared_draft), len(compared_final))
    distance = Levenshtein.distance(compared_draft, compared_final)
    ratio = distance / denominator if denominator else 0.0

    if ratio == 0:
        grade = Grade.UNCHANGED
    elif ratio <= 0.1:
        grade = Grade.LIGHT
    elif ratio <= 0.4:
        grade = Grade.MEDIUM
    else:
        grade = Grade.REWRITE

    draft_sentences = Counter(_sentences(draft))
    final_sentences = Counter(_sentences(final))
    matched = sum((draft_sentences & final_sentences).values())
    draft_count = sum(draft_sentences.values())
    final_count = sum(final_sentences.values())

    return EditMetrics(
        kind="text",
        edit_ratio=ratio,
        grade=grade,
        kept_sentence_ratio=matched / draft_count if draft_count else 1.0,
        deleted_sentences=draft_count - matched,
        added_sentences=final_count - matched,
    )
