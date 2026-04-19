import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_CLOUD_ACCESS_KEY_ID_PATTERN = re.compile(r"\b(?:AKIA|ASIA|AIDA|AROA)[0-9A-Z]{16}\b")


class CloudAccessKeyIdRecognizer(BaseRecognizer):
    entity_type = EntityType.cloud_access_key_id
    source = "cloud_access_key_id_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        return [
            Detection(
                entity_type=self.entity_type,
                start=match.start(),
                end=match.end(),
                text=match.group(0),
                confidence=0.998,
                source=self.source,
            )
            for match in _CLOUD_ACCESS_KEY_ID_PATTERN.finditer(text)
        ]
