import re

from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_URI_WITH_CREDENTIALS_PATTERN = re.compile(
    r"\b[A-Za-z][A-Za-z0-9+.-]*://[^\s:/?#@]+:[^@\s/]+@[^\s'\";]+"
)

_DB_DSN_PATTERN = re.compile(
    r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqp|kafka|sqlserver|mssql|oracle)://"
    r"(?=[^\s'\";]*(?::[^@\s/]+@|[?&](?:password|pwd|pass)=))[^\s'\";]+",
    re.IGNORECASE,
)

_SEMICOLON_CONNSTR_PATTERN = re.compile(
    r"\b(?:server|data source|host)\s*=\s*[^;]+;[^;\n]*(?:password|pwd)\s*=\s*[^;]+(?:;|$)",
    re.IGNORECASE,
)


class ConnectionStringRecognizer(BaseRecognizer):
    entity_type = EntityType.connection_string
    source = "connection_string_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        detections.extend(self._from_pattern(text, _URI_WITH_CREDENTIALS_PATTERN, 0.998))
        detections.extend(self._from_pattern(text, _DB_DSN_PATTERN, 0.996))
        detections.extend(self._from_pattern(text, _SEMICOLON_CONNSTR_PATTERN, 0.997))
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
