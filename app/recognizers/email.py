import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_EMAIL_PATTERN = re.compile(
    r"(?<![\\w.])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,})(?![\\w.])"
)


class EmailRegexRecognizer(BaseRecognizer):
    entity_type = EntityType.email
    source = "email_regex_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        return [
            Detection(
                entity_type=self.entity_type,
                start=match.start(1),
                end=match.end(1),
                text=match.group(1),
                confidence=0.995,
                source=self.source,
            )
            for match in _EMAIL_PATTERN.finditer(text)
        ]
