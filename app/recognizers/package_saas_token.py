import re
from dataclasses import dataclass

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer


@dataclass(frozen=True, slots=True)
class TokenPattern:
    pattern: re.Pattern[str]
    confidence: float


_PACKAGE_SAAS_PATTERNS: tuple[TokenPattern, ...] = (
    TokenPattern(pattern=re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"), confidence=0.998),
    TokenPattern(pattern=re.compile(r"\bpypi-[A-Za-z0-9._-]{50,255}\b"), confidence=0.997),
    TokenPattern(pattern=re.compile(r"\bglpat-[A-Za-z0-9\-_]{20,255}\b"), confidence=0.997),
    TokenPattern(pattern=re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,255}\b"), confidence=0.997),
)


class PackageSaasTokenRecognizer(BaseRecognizer):
    entity_type = EntityType.package_saas_token
    source = "package_saas_token_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for entry in _PACKAGE_SAAS_PATTERNS:
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
