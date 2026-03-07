from functools import lru_cache

from app.config.settings import get_settings
from app.detection.pipeline import DetectionPipeline
from app.replacement.pseudonymizer import TextPseudonymizer
from app.reversal.depseudonymizer import TextDepseudonymizer


@lru_cache
def get_detection_pipeline() -> DetectionPipeline:
    return DetectionPipeline.default(get_settings())


@lru_cache
def get_pseudonymizer() -> TextPseudonymizer:
    return TextPseudonymizer()


@lru_cache
def get_depseudonymizer() -> TextDepseudonymizer:
    return TextDepseudonymizer()
