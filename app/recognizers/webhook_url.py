import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_SLACK_WEBHOOK_PATTERN = re.compile(
    r"\bhttps://hooks\.slack\.com/services/[A-Za-z0-9/_-]{20,}\b"
)

_DISCORD_WEBHOOK_PATTERN = re.compile(
    r"\bhttps://discord(?:app)?\.com/api/webhooks/\d{8,}/[A-Za-z0-9._-]{20,}\b"
)


class WebhookUrlRecognizer(BaseRecognizer):
    entity_type = EntityType.webhook_url
    source = "webhook_url_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        detections.extend(self._from_pattern(text, _SLACK_WEBHOOK_PATTERN, 0.999))
        detections.extend(self._from_pattern(text, _DISCORD_WEBHOOK_PATTERN, 0.999))
        return detections

    def _from_pattern(
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
