from abc import ABC, abstractmethod

from app.detection.types import Detection, EntityType


class BaseRecognizer(ABC):
    entity_type: EntityType
    source: str
    supported_languages: set[str] = {"en", "nl"}

    def supports_language(self, language: str) -> bool:
        return language in self.supported_languages

    @abstractmethod
    def detect(self, text: str, language: str) -> list[Detection]:
        raise NotImplementedError
