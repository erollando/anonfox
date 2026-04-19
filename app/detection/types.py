from dataclasses import dataclass
from enum import Enum


class EntityType(str, Enum):
    person = "person"
    phone = "phone"
    email = "email"
    bearer_token = "bearer_token"
    private_key = "private_key"
    api_key = "api_key"
    connection_string = "connection_string"
    jwt = "jwt"
    webhook_secret = "webhook_secret"
    oauth_cloud_token = "oauth_cloud_token"
    session_token = "session_token"
    cloud_credential = "cloud_credential"
    package_saas_token = "package_saas_token"
    generic_secret = "generic_secret"
    webhook_url = "webhook_url"
    auth_header_token = "auth_header_token"
    cloud_access_key_id = "cloud_access_key_id"
    cloud_secret_key_assignment = "cloud_secret_key_assignment"
    private_key_inline = "private_key_inline"


_ENTITY_CLASS_ALIASES: dict[str, EntityType] = {
    "person": EntityType.person,
    "people": EntityType.person,
    "per": EntityType.person,
    "phone": EntityType.phone,
    "phone_number": EntityType.phone,
    "phonenumber": EntityType.phone,
    "tel": EntityType.phone,
    "telephone": EntityType.phone,
    "email": EntityType.email,
    "mail": EntityType.email,
    "bearer": EntityType.bearer_token,
    "bearer_token": EntityType.bearer_token,
    "private_key": EntityType.private_key,
    "pem_private_key": EntityType.private_key,
    "api_key": EntityType.api_key,
    "apikey": EntityType.api_key,
    "connection_string": EntityType.connection_string,
    "connectionstring": EntityType.connection_string,
    "dsn": EntityType.connection_string,
    "database_url": EntityType.connection_string,
    "db_url": EntityType.connection_string,
    "jwt": EntityType.jwt,
    "json_web_token": EntityType.jwt,
    "webhook_secret": EntityType.webhook_secret,
    "webhooksigningsecret": EntityType.webhook_secret,
    "whsec": EntityType.webhook_secret,
    "oauth_cloud_token": EntityType.oauth_cloud_token,
    "oauth_token": EntityType.oauth_cloud_token,
    "cloud_token": EntityType.oauth_cloud_token,
    "session_token": EntityType.session_token,
    "auth_cookie": EntityType.session_token,
    "session_cookie": EntityType.session_token,
    "cloud_credential": EntityType.cloud_credential,
    "cloud_credentials": EntityType.cloud_credential,
    "package_saas_token": EntityType.package_saas_token,
    "package_token": EntityType.package_saas_token,
    "saas_token": EntityType.package_saas_token,
    "generic_secret": EntityType.generic_secret,
    "opaque_secret": EntityType.generic_secret,
    "webhook_url": EntityType.webhook_url,
    "auth_header_token": EntityType.auth_header_token,
    "header_token": EntityType.auth_header_token,
    "cloud_access_key_id": EntityType.cloud_access_key_id,
    "cloud_secret_key_assignment": EntityType.cloud_secret_key_assignment,
    "private_key_inline": EntityType.private_key_inline,
}


def normalize_class_name(value: str) -> EntityType:
    normalized = value.strip().lower()
    try:
        return _ENTITY_CLASS_ALIASES[normalized]
    except KeyError as exc:
        supported = ", ".join(sorted(set(v.value for v in _ENTITY_CLASS_ALIASES.values())))
        raise ValueError(f"Unsupported class '{value}'. Supported classes: {supported}") from exc


@dataclass(frozen=True, slots=True)
class Detection:
    entity_type: EntityType
    start: int
    end: int
    text: str
    confidence: float
    source: str

    @property
    def span_length(self) -> int:
        return self.end - self.start
