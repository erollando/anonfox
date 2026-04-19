import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_INLINE_PRIVATE_KEY_PATTERN = re.compile(
    r"(?i)\b(?:private_key|privatekey|client_private_key|signing_key)\b\s*[:=]\s*([A-Za-z0-9._\-+/=]{20,})"
)


class PrivateKeyInlineRecognizer(BaseRecognizer):
    entity_type = EntityType.private_key_inline
    source = "private_key_inline_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        return [
            Detection(
                entity_type=self.entity_type,
                start=match.start(1),
                end=match.end(1),
                text=match.group(1),
                confidence=0.993,
                source=self.source,
            )
            for match in _INLINE_PRIVATE_KEY_PATTERN.finditer(text)
        ]
