from dataclasses import dataclass
from enum import Enum


class EntityType(str, Enum):
    person = "person"
    phone = "phone"
    email = "email"


_ENTITY_CLASS_ALIASES: dict[str, EntityType] = {
    "person": EntityType.person,
    "people": EntityType.person,
    "per": EntityType.person,
    "phone": EntityType.phone,
    "phone_number": EntityType.phone,
    "phonenumber": EntityType.phone,
    "tel": EntityType.phone,
    "telephone": EntityType.phone,
    "email": EntityType.email,
    "mail": EntityType.email,
}


def normalize_class_name(value: str) -> EntityType:
    normalized = value.strip().lower()
    try:
        return _ENTITY_CLASS_ALIASES[normalized]
    except KeyError as exc:
        supported = ", ".join(sorted(set(v.value for v in _ENTITY_CLASS_ALIASES.values())))
        raise ValueError(f"Unsupported class '{value}'. Supported classes: {supported}") from exc


@dataclass(frozen=True, slots=True)
class Detection:
    entity_type: EntityType
    start: int
    end: int
    text: str
    confidence: float
    source: str

    @property
    def span_length(self) -> int:
        return self.end - self.start
