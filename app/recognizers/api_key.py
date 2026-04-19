import re
from dataclasses import dataclass

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer


@dataclass(frozen=True, slots=True)
class VendorPattern:
    pattern: re.Pattern[str]
    confidence: float


_KNOWN_VENDOR_PATTERNS: tuple[VendorPattern, ...] = (
    VendorPattern(pattern=re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), confidence=0.999),
    VendorPattern(pattern=re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), confidence=0.999),
    VendorPattern(pattern=re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,255}\b"), confidence=0.999),
    VendorPattern(pattern=re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,255}\b"), confidence=0.998),
    VendorPattern(pattern=re.compile(r"\bpk_(?:live|test)_[A-Za-z0-9]{16,255}\b"), confidence=0.997),
    VendorPattern(pattern=re.compile(r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b"), confidence=0.998),
)


class ApiKeyRecognizer(BaseRecognizer):
    entity_type = EntityType.api_key
    source = "api_key_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for entry in _KNOWN_VENDOR_PATTERNS:
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
