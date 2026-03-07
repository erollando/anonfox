from __future__ import annotations

import re
from abc import ABC, abstractmethod

from app.config.settings import Settings
from app.detection.types import Detection, EntityType
from app.recognizers.base import BaseRecognizer

_TITLE_PATTERN = re.compile(
    r"(?i)\b(?:mr|mrs|ms|dr|prof|sir|madam|meneer|mevrouw|dhr|mevr)\.?\s+"
    r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’-]*(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’-]*){0,1}"
)

_CAPITALIZED_PATTERN = re.compile(
    r"\b[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’-]+"
    r"(?:\s+(?:van|de|den|der|ter|ten|von|di|da|del|du|la|le|[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’-]+)){1,3}\b"
)

_LOWERCASE_PATTERN = re.compile(
    r"\b[a-zà-öø-ÿ][a-zà-öø-ÿ'’-]{1,}(?:\s+[a-zà-öø-ÿ][a-zà-öø-ÿ'’-]{1,}){1,2}\b"
)

_PARTICLES = {
    "van",
    "de",
    "den",
    "der",
    "ter",
    "ten",
    "von",
    "di",
    "da",
    "del",
    "du",
    "la",
    "le",
}

_STOPWORDS = {
    "and",
    "the",
    "this",
    "that",
    "with",
    "without",
    "from",
    "has",
    "have",
    "told",
    "number",
    "phone",
    "his",
    "her",
    "in",
    "is",
    "zijn",
    "haar",
    "met",
    "en",
    "de",
    "het",
    "een",
    "dit",
    "dat",
    "heeft",
    "verteld",
    "nummer",
    "telefoon",
    "tekst",
}

_NAME_HINTS = {
    "pino",
    "daniele",
    "john",
    "jane",
    "anna",
    "emma",
    "liam",
    "noah",
    "peter",
    "maria",
    "jan",
    "piet",
    "kees",
    "sanne",
}

_CONTEXT_CUES = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "meneer",
    "mevrouw",
    "dhr",
    "mevr",
    "told",
    "said",
    "called",
    "spoke",
    "number",
    "phone",
    "contact",
    "vertelde",
    "zei",
    "belde",
    "sprak",
    "nummer",
    "telefoon",
    "contact",
}


def _normalized_tokens(candidate: str) -> list[str]:
    return [token.strip(".'").lower() for token in candidate.split() if token]


def _should_skip_person_candidate(candidate: str) -> bool:
    tokens = _normalized_tokens(candidate)
    if not tokens:
        return True
    if len(tokens) == 1 and tokens[0] in _STOPWORDS:
        return True
    if all(token in _STOPWORDS for token in tokens):
        return True
    return False


class BasePersonNerProvider(ABC):
    @abstractmethod
    def detect(self, text: str, language: str) -> list[Detection]:
        raise NotImplementedError


class SpacyPersonNerProvider(BasePersonNerProvider):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pipelines: dict[str, object | None] = {}

    def _load_pipeline(self, language: str) -> object | None:
        if language in self._pipelines:
            return self._pipelines[language]

        if not self._settings.enable_spacy_ner:
            self._pipelines[language] = None
            return None

        model_name = (
            self._settings.spacy_model_nl if language == "nl" else self._settings.spacy_model_en
        )

        try:
            import spacy

            self._pipelines[language] = spacy.load(model_name)
        except Exception:
            self._pipelines[language] = None
        return self._pipelines[language]

    def detect(self, text: str, language: str) -> list[Detection]:
        pipeline = self._load_pipeline(language)
        if pipeline is None:
            return []

        detections: list[Detection] = []
        doc = pipeline(text)
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "PER"}:
                if _should_skip_person_candidate(ent.text):
                    continue
                detections.append(
                    Detection(
                        entity_type=EntityType.person,
                        start=ent.start_char,
                        end=ent.end_char,
                        text=ent.text,
                        confidence=0.88,
                        source="spacy_person_recognizer",
                    )
                )
        return detections


class HeuristicPersonRecognizer(BaseRecognizer):
    entity_type = EntityType.person
    source = "hybrid_person_recognizer"

    def detect(self, text: str, language: str) -> list[Detection]:
        detections: list[Detection] = []
        detections.extend(self._title_matches(text))
        detections.extend(self._capitalized_matches(text))
        detections.extend(self._lowercase_matches(text))
        return detections

    def _title_matches(self, text: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _TITLE_PATTERN.finditer(text):
            candidate = match.group(0).strip()
            tokens = _normalized_tokens(candidate)
            if len(tokens) < 2:
                continue
            if tokens[-1] in _STOPWORDS:
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(),
                    end=match.end(),
                    text=candidate,
                    confidence=0.98,
                    source=self.source,
                )
            )
        return detections

    def _capitalized_matches(self, text: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _CAPITALIZED_PATTERN.finditer(text):
            candidate = match.group(0)
            tokens = _normalized_tokens(candidate)
            if any(token in _STOPWORDS for token in tokens):
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(),
                    end=match.end(),
                    text=candidate,
                    confidence=0.82,
                    source=self.source,
                )
            )
        return detections

    def _lowercase_matches(self, text: str) -> list[Detection]:
        detections: list[Detection] = []
        for match in _LOWERCASE_PATTERN.finditer(text):
            candidate = match.group(0)
            tokens = _normalized_tokens(candidate)
            if any(token in _STOPWORDS for token in tokens):
                continue
            if not any(token in _NAME_HINTS for token in tokens):
                continue

            left_index = max(0, match.start() - 25)
            right_index = min(len(text), match.end() + 25)
            context = text[left_index:right_index].lower()
            if not any(cue in context for cue in _CONTEXT_CUES):
                continue

            detections.append(
                Detection(
                    entity_type=self.entity_type,
                    start=match.start(),
                    end=match.end(),
                    text=candidate,
                    confidence=0.74,
                    source=self.source,
                )
            )
        return detections


class SpacyPersonRecognizer(BaseRecognizer):
    entity_type = EntityType.person
    source = "spacy_person_recognizer"

    def __init__(self, provider: BasePersonNerProvider) -> None:
        self._provider = provider

    def detect(self, text: str, language: str) -> list[Detection]:
        return self._provider.detect(text, language)
