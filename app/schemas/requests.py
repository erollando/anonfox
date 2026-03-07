from pydantic import BaseModel, Field, field_validator

from app.detection.types import normalize_class_name
from app.schemas.common import LanguageCode, PersonMode


class PseudonymizeOptions(BaseModel):
    return_mapping: bool = True
    include_detections: bool = False
    person_mode: PersonMode = PersonMode.full_span


class PseudonymizeRequest(BaseModel):
    text: str = Field(min_length=1)
    classes: list[str] = Field(default_factory=lambda: ["person", "phone"])
    language: LanguageCode = LanguageCode.en
    options: PseudonymizeOptions = Field(default_factory=PseudonymizeOptions)

    @field_validator("classes")
    @classmethod
    def validate_classes(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("At least one class must be selected")

        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            canonical = normalize_class_name(item).value
            if canonical not in seen:
                seen.add(canonical)
                normalized.append(canonical)
        return normalized


class DepseudonymizeRequest(BaseModel):
    text: str = Field(min_length=1)
    mapping: dict[str, str] = Field(min_length=1)

    @field_validator("mapping")
    @classmethod
    def validate_mapping(cls, value: dict[str, str]) -> dict[str, str]:
        for placeholder, original in value.items():
            if not placeholder.startswith("@"):
                raise ValueError("Mapping keys must start with '@'")
            if original == "":
                raise ValueError("Mapping values cannot be empty strings")
        return value
