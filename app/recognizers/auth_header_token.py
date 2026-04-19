import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_AUTHORIZATION_TOKEN_PATTERN = re.compile(
    r"(?i)\bauthorization\s*:\s*(?:token|basic)\s+([A-Za-z0-9._\-+/=]{12,})"
)

_APIKEY_HEADER_PATTERN = re.compile(
    r"(?i)\b(?:x-api-key|api-key|apikey)\s*:\s*([A-Za-z0-9._\-+/=]{12,})"
)


class AuthHeaderTokenRecognizer(BaseRecognizer):
    entity_type = EntityType.auth_header_token
    source = "auth_header_token_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        detections.extend(self._from_pattern(text, _AUTHORIZATION_TOKEN_PATTERN, 0.997))
        detections.extend(self._from_pattern(text, _APIKEY_HEADER_PATTERN, 0.997))
        return detections

    def _from_pattern(
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
