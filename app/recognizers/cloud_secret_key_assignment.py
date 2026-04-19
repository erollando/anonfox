import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_ASSIGNMENT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\baws_secret_access_key\b\s*[:=]\s*([A-Za-z0-9/+=]{30,64})"),
    re.compile(r"(?i)\bsecret_access_key\b\s*[:=]\s*([A-Za-z0-9/+=]{30,64})"),
    re.compile(r"(?i)\baws_session_token\b\s*[:=]\s*([A-Za-z0-9/+=]{40,})"),
)


class CloudSecretKeyAssignmentRecognizer(BaseRecognizer):
    entity_type = EntityType.cloud_secret_key_assignment
    source = "cloud_secret_key_assignment_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for pattern in _ASSIGNMENT_PATTERNS:
            for match in pattern.finditer(text):
                detections.append(
                    Detection(
                        entity_type=self.entity_type,
                        start=match.start(1),
                        end=match.end(1),
                        text=match.group(1),
                        confidence=0.999,
                        source=self.source,
                    )
                )
        return detections
