import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_BEARER_PATTERN = re.compile(
    r"(?i)\bbearer\s+([A-Za-z0-9\-._~+/]+=*)(?=$|[\s'\",;])"
)


class BearerTokenRecognizer(BaseRecognizer):
    entity_type = EntityType.bearer_token
    source = "bearer_token_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _BEARER_PATTERN.finditer(text):
            token = match.group(1)
            if len(token) < 16:
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(1),
                    end=match.end(1),
                    text=token,
                    confidence=0.998,
                    source=self.source,
                )
            )
        return detections
