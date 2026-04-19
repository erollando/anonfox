import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_AWS_ACCESS_KEY_ID_PATTERN = re.compile(r"\b(?:AKIA|ASIA|AIDA|AROA)[0-9A-Z]{16}\b")

_AWS_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\baws_secret_access_key\b\s*[:=]\s*([A-Za-z0-9/+=]{30,64})"
)

_AWS_SESSION_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\baws_session_token\b\s*[:=]\s*([A-Za-z0-9/+=]{40,})"
)

_AWS_ACCESS_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\baws_access_key_id\b\s*[:=]\s*([A-Z0-9]{16,32})"
)


class CloudCredentialRecognizer(BaseRecognizer):
    entity_type = EntityType.cloud_credential
    source = "cloud_credential_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        detections.extend(self._extract_whole(text, _AWS_ACCESS_KEY_ID_PATTERN, 0.998))
        detections.extend(self._extract_group(text, _AWS_SECRET_ASSIGNMENT_PATTERN, 0.999))
        detections.extend(self._extract_group(text, _AWS_SESSION_ASSIGNMENT_PATTERN, 0.998))
        detections.extend(self._extract_group(text, _AWS_ACCESS_ASSIGNMENT_PATTERN, 0.998))
        return detections

    def _extract_whole(
        self, text: str, pattern: re.Pattern[str], confidence: float
    ) -> list[Detection]:
        return [
            Detection(
                entity_type=self.entity_type,
                start=match.start(),
                end=match.end(),
                text=match.group(0),
                confidence=confidence,
                source=self.source,
            )
            for match in pattern.finditer(text)
        ]

    def _extract_group(
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
