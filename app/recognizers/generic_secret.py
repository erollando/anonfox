import math
import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_CONTEXTUAL_SECRET_PATTERN = re.compile(
    r"(?i)\b(?:token|secret|api[_-]?key|auth(?:orization)?|auth[_-]?secret|credential|passwd|password|pwd)\b"
    r"[^\n]{0,24}(?:=|:)\s*([A-Za-z0-9._\-+/=]{16,})"
)

_WEAK_WORDS = {
    "changeme",
    "password",
    "secret",
    "token",
    "example",
    "test",
    "dummy",
    "sample",
}


def _shannon_entropy(value: str) -> float:
    counts: dict[str, int] = {}
    for char in value:
        counts[char] = counts.get(char, 0) + 1
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _has_varied_charset(value: str) -> bool:
    classes = 0
    classes += any(c.islower() for c in value)
    classes += any(c.isupper() for c in value)
    classes += any(c.isdigit() for c in value)
    classes += any(not c.isalnum() for c in value)
    return classes >= 3


class GenericSecretRecognizer(BaseRecognizer):
    entity_type = EntityType.generic_secret
    source = "generic_secret_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _CONTEXTUAL_SECRET_PATTERN.finditer(text):
            candidate = match.group(1)
            normalized = candidate.lower()
            if normalized in _WEAK_WORDS:
                continue
            if len(candidate) < 20:
                continue
            if _shannon_entropy(candidate) < 3.5:
                continue
            if not _has_varied_charset(candidate):
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(1),
                    end=match.end(1),
                    text=candidate,
                    confidence=0.75,
                    source=self.source,
                )
            )
        return detections
