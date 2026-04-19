import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_JWT_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,})(?![A-Za-z0-9_-])"
)


class JwtRecognizer(BaseRecognizer):
    entity_type = EntityType.jwt
    source = "jwt_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _JWT_PATTERN.finditer(text):
            token = match.group(1)

            # Reject obvious decimal/IP-like triples to keep precision high.
            if all(part.isdigit() for part in token.split(".")):
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(1),
                    end=match.end(1),
                    text=token,
                    confidence=0.996,
                    source=self.source,
                )
            )
        return detections
