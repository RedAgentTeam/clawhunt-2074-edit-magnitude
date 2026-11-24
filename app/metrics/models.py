from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Kind(StrEnum):
    TEXT = "text"
    STRUCTURED = "structured"


class Grade(StrEnum):
    UNCHANGED = "unchanged"
    LIGHT = "light"
    MEDIUM = "medium"
    REWRITE = "rewrite"


class ListChange(BaseModel):
    added: int = Field(default=0, ge=0)
    removed: int = Field(default=0, ge=0)
    modified: int = Field(default=0, ge=0)


class EditMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["text", "structured"]
    edit_ratio: float | None = Field(default=None, ge=0, le=1)
    grade: Grade | None = None
    kept_sentence_ratio: float | None = Field(default=None, ge=0, le=1)
    deleted_sentences: int | None = Field(default=None, ge=0)
    added_sentences: int | None = Field(default=None, ge=0)
    field_edit_ratio: float | None = Field(default=None, ge=0, le=1)
    changed_fields: int | None = Field(default=None, ge=0)
    total_fields: int | None = Field(default=None, ge=0)
    list_changes: dict[str, ListChange] | None = None
    critical_edits: int | None = Field(default=None, ge=0)
