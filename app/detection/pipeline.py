from app.config.settings import Settings
from app.detection.language import normalize_language
from app.detection.overlap import resolve_overlaps
from app.detection.registry import RecognizerRegistry
from app.detection.types import Detection, normalize_class_name
from app.recognizers.email import EmailRegexRecognizer
from app.recognizers.person import (
    HeuristicPersonRecognizer,
    SpacyPersonNerProvider,
    SpacyPersonRecognizer,
)
from app.recognizers.phone import PhoneRegexRecognizer


class DetectionPipeline:
    def __init__(self, registry: RecognizerRegistry) -> None:
        self._registry = registry

    @classmethod
    def default(cls, settings: Settings) -> "DetectionPipeline":
        registry = RecognizerRegistry()
        registry.register(PhoneRegexRecognizer())
        registry.register(EmailRegexRecognizer())
        registry.register(HeuristicPersonRecognizer())
        registry.register(SpacyPersonRecognizer(provider=SpacyPersonNerProvider(settings)))
        return cls(registry)

    def supported_classes(self) -> list[str]:
        return self._registry.supported_classes()

    def analyze(self, text: str, classes: list[str], language: str) -> list[Detection]:
        normalized_language = normalize_language(language)

        raw_detections: list[Detection] = []
        for class_name in classes:
            entity_type = normalize_class_name(class_name)
            for recognizer in self._registry.get(entity_type, normalized_language):
                raw_detections.extend(recognizer.detect(text, normalized_language))

        deduped = self._deduplicate(raw_detections)
        return resolve_overlaps(deduped)

    def _deduplicate(self, detections: list[Detection]) -> list[Detection]:
        best_by_span: dict[tuple[str, int, int, str], Detection] = {}
        for detection in detections:
            key = (
                detection.entity_type.value,
                detection.start,
                detection.end,
                detection.text,
            )
            existing = best_by_span.get(key)
            if existing is None or detection.confidence > existing.confidence:
                best_by_span[key] = detection
        return list(best_by_span.values())
