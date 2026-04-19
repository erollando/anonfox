from app.config.settings import Settings
from app.detection.language import normalize_language
from app.detection.overlap import resolve_overlaps
from app.detection.registry import RecognizerRegistry
from app.detection.types import Detection, normalize_class_name
from app.recognizers.api_key import ApiKeyRecognizer
from app.recognizers.auth_header_token import AuthHeaderTokenRecognizer
from app.recognizers.bearer_token import BearerTokenRecognizer
from app.recognizers.cloud_access_key_id import CloudAccessKeyIdRecognizer
from app.recognizers.cloud_credential import CloudCredentialRecognizer
from app.recognizers.cloud_secret_key_assignment import CloudSecretKeyAssignmentRecognizer
from app.recognizers.connection_string import ConnectionStringRecognizer
from app.recognizers.email import EmailRegexRecognizer
from app.recognizers.generic_secret import GenericSecretRecognizer
from app.recognizers.jwt import JwtRecognizer
from app.recognizers.oauth_cloud_token import OAuthCloudTokenRecognizer
from app.recognizers.package_saas_token import PackageSaasTokenRecognizer
from app.recognizers.person import (
    HeuristicPersonRecognizer,
    SpacyPersonNerProvider,
    SpacyPersonRecognizer,
)
from app.recognizers.phone import PhoneRegexRecognizer
from app.recognizers.private_key import PrivateKeyRecognizer
from app.recognizers.private_key_inline import PrivateKeyInlineRecognizer
from app.recognizers.session_token import SessionTokenRecognizer
from app.recognizers.webhook_url import WebhookUrlRecognizer
from app.recognizers.webhook_secret import WebhookSecretRecognizer


class DetectionPipeline:
    def __init__(self, registry: RecognizerRegistry) -> None:
        self._registry = registry

    @classmethod
    def default(cls, settings: Settings) -> "DetectionPipeline":
        registry = RecognizerRegistry()
        registry.register(PhoneRegexRecognizer())
        registry.register(EmailRegexRecognizer())
        registry.register(BearerTokenRecognizer())
        registry.register(AuthHeaderTokenRecognizer())
        registry.register(PrivateKeyRecognizer())
        registry.register(PrivateKeyInlineRecognizer())
        registry.register(ApiKeyRecognizer())
        registry.register(ConnectionStringRecognizer())
        registry.register(JwtRecognizer())
        registry.register(WebhookSecretRecognizer())
        registry.register(WebhookUrlRecognizer())
        registry.register(OAuthCloudTokenRecognizer())
        registry.register(SessionTokenRecognizer())
        registry.register(CloudAccessKeyIdRecognizer())
        registry.register(CloudSecretKeyAssignmentRecognizer())
        registry.register(CloudCredentialRecognizer())
        registry.register(PackageSaasTokenRecognizer())
        registry.register(GenericSecretRecognizer())
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
