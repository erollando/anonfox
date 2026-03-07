from app.detection.types import Detection, EntityType


_ENTITY_PRIORITY: dict[EntityType, int] = {
    EntityType.phone: 100,
    EntityType.email: 95,
    EntityType.person: 90,
}


def _overlaps(a: Detection, b: Detection) -> bool:
    return not (a.end <= b.start or b.end <= a.start)


def _rank(detection: Detection) -> tuple[float, float, float, str]:
    priority = _ENTITY_PRIORITY.get(detection.entity_type, 10)
    return (
        float(priority),
        float(detection.confidence),
        float(detection.span_length),
        detection.source,
    )


def resolve_overlaps(detections: list[Detection]) -> list[Detection]:
    ordered = sorted(
        detections,
        key=lambda item: (
            item.start,
            -item.span_length,
            -_ENTITY_PRIORITY.get(item.entity_type, 10),
            -item.confidence,
            item.source,
        ),
    )

    accepted: list[Detection] = []
    for candidate in ordered:
        conflicting_indexes = [
            index for index, existing in enumerate(accepted) if _overlaps(candidate, existing)
        ]
        if not conflicting_indexes:
            accepted.append(candidate)
            continue

        candidate_rank = _rank(candidate)
        if all(candidate_rank > _rank(accepted[index]) for index in conflicting_indexes):
            accepted = [
                existing for existing in accepted if not _overlaps(existing, candidate)
            ]
            accepted.append(candidate)

    return sorted(accepted, key=lambda item: (item.start, item.end))
