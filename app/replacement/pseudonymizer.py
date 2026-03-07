from collections import defaultdict
from dataclasses import dataclass

from app.detection.types import Detection, EntityType
from app.replacement.placeholders import build_placeholder


@dataclass(frozen=True, slots=True)
class AppliedDetection:
    detection: Detection
    placeholder: str


@dataclass(frozen=True, slots=True)
class PseudonymizeResult:
    text: str
    mapping: dict[str, str]
    applied_detections: list[AppliedDetection]


class TextPseudonymizer:
    def pseudonymize(self, text: str, detections: list[Detection]) -> PseudonymizeResult:
        sorted_detections = sorted(detections, key=lambda item: (item.start, item.end))

        counters: dict[EntityType, int] = defaultdict(int)
        value_to_placeholder: dict[tuple[EntityType, str], str] = {}
        mapping: dict[str, str] = {}
        applied: list[AppliedDetection] = []

        for detection in sorted_detections:
            key = (detection.entity_type, detection.text)
            placeholder = value_to_placeholder.get(key)
            if placeholder is None:
                counters[detection.entity_type] += 1
                placeholder = build_placeholder(detection.entity_type, counters[detection.entity_type])
                value_to_placeholder[key] = placeholder
                mapping[placeholder] = detection.text

            applied.append(AppliedDetection(detection=detection, placeholder=placeholder))

        output = text
        for item in sorted(applied, key=lambda row: row.detection.start, reverse=True):
            start = item.detection.start
            end = item.detection.end
            output = f"{output[:start]}{item.placeholder}{output[end:]}"

        return PseudonymizeResult(text=output, mapping=mapping, applied_detections=applied)
