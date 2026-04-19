import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_WEBHOOK_SECRET_PATTERN = re.compile(
    r"\b((?:[a-z]{2,12}_)?whsec_[A-Za-z0-9]{16,255})\b",
    re.IGNORECASE,
)


class WebhookSecretRecognizer(BaseRecognizer):
    entity_type = EntityType.webhook_secret
    source = "webhook_secret_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        return [
            Detection(
                entity_type=self.entity_type,
                start=match.start(1),
                end=match.end(1),
                text=match.group(1),
                confidence=0.999,
                source=self.source,
            )
            for match in _WEBHOOK_SECRET_PATTERN.finditer(text)
        ]
