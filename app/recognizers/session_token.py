import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_SESSION_FIELD_PATTERN = re.compile(
    r"(?i)\b(?:session(?:id|_id)?|sid|auth(?:_token|token)?|access_token|refresh_token|id_token)"
    r"\b\s*[:=]\s*([A-Za-z0-9._\-+/=]{16,})"
)

_COOKIE_HEADER_PATTERN = re.compile(
    r"(?i)\b(?:set-cookie|cookie)\s*:\s*[^=\s;]{2,64}=([A-Za-z0-9._\-+/=]{16,})"
)


class SessionTokenRecognizer(BaseRecognizer):
    entity_type = EntityType.session_token
    source = "session_token_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        detections.extend(self._extract(text, _SESSION_FIELD_PATTERN, 0.992))
        detections.extend(self._extract(text, _COOKIE_HEADER_PATTERN, 0.996))
        return detections

    def _extract(
        self, text: str, pattern: re.Pattern[str], confidence: float
    ) -> list[Detection]:
        return [
            Detection(
                entity_type=self.entity_type,
                start=match.start(1),
                end=match.end(1),
                text=match.group(1),
                confidence=confidence,
                source=self.source,
            )
            for match in pattern.finditer(text)
        ]
