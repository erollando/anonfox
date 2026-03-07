import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s./-]?)?(?:\(?\d{1,4}\)?[\s./-]?){1,4}\d{2,4}(?!\w)",
)


class PhoneRegexRecognizer(BaseRecognizer):
    entity_type = EntityType.phone
    source = "phone_regex_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _PHONE_PATTERN.finditer(text):
            candidate = match.group(0)
            digits_only = re.sub(r"\D", "", candidate)

            if len(digits_only) < 7 or len(digits_only) > 15:
                continue
            if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", candidate):
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(),
                    end=match.end(),
                    text=candidate,
                    confidence=0.999,
                    source=self.source,
                )
            )
        return detections
