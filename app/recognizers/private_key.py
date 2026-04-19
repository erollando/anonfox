import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_PRIVATE_KEY_BLOCK_PATTERN = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----[\s\S]+?-----END (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"
)


class PrivateKeyRecognizer(BaseRecognizer):
    entity_type = EntityType.private_key
    source = "private_key_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _PRIVATE_KEY_BLOCK_PATTERN.finditer(text):
            candidate = match.group(0)
            if "\n" not in candidate:
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(),
                    end=match.end(),
                    text=candidate,
                    confidence=1.0,
                    source=self.source,
                )
            )
        return detections
