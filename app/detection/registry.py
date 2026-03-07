from collections import defaultdict

from app.detection.types import EntityType
from app.recognizers.base import BaseRecognizer


class RecognizerRegistry:
    def __init__(self) -> None:
        self._recognizers: dict[EntityType, list[BaseRecognizer]] = defaultdict(list)

    def register(self, recognizer: BaseRecognizer) -> None:
        self._recognizers[recognizer.entity_type].append(recognizer)

    def get(self, entity_type: EntityType, language: str) -> list[BaseRecognizer]:
        return [
            recognizer
            for recognizer in self._recognizers.get(entity_type, [])
            if recognizer.supports_language(language)
        ]

    def supported_classes(self) -> list[str]:
        return sorted(entity_type.value for entity_type in self._recognizers.keys())
