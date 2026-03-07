from app.detection.types import EntityType

_PLACEHOLDER_PREFIX = {
    EntityType.person: "person",
    EntityType.phone: "phone",
    EntityType.email: "email",
}


def build_placeholder(entity_type: EntityType, index: int) -> str:
    prefix = _PLACEHOLDER_PREFIX[entity_type]
    return f"@{prefix}{index}"
