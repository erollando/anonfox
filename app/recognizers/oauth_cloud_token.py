import re
from dataclasses import dataclass

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer


@dataclass(frozen=True, slots=True)
class TokenPattern:
    pattern: re.Pattern[str]
    confidence: float


_KNOWN_PREFIX_PATTERNS: tuple[TokenPattern, ...] = (
    TokenPattern(pattern=re.compile(r"\bya29\.[A-Za-z0-9\-_]{20,}\b"), confidence=0.999),
    TokenPattern(pattern=re.compile(r"\bgho_[A-Za-z0-9]{20,255}\b"), confidence=0.998),
    TokenPattern(pattern=re.compile(r"\bghu_[A-Za-z0-9]{20,255}\b"), confidence=0.998),
    TokenPattern(pattern=re.compile(r"\bghs_[A-Za-z0-9]{20,255}\b"), confidence=0.998),
)


class OAuthCloudTokenRecognizer(BaseRecognizer):
    entity_type = EntityType.oauth_cloud_token
    source = "oauth_cloud_token_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for entry in _KNOWN_PREFIX_PATTERNS:
            for match in entry.pattern.finditer(text):
                detections.append(
                    Detection(
                        entity_type=self.entity_type,
                        start=match.start(),
                        end=match.end(),
                        text=match.group(0),
                        confidence=entry.confidence,
                        source=self.source,
                    )
                )
        return detections
