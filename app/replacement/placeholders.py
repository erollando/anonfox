from app.detection.types import EntityType

_PLACEHOLDER_PREFIX = {
    EntityType.person: "person",
    EntityType.phone: "phone",
    EntityType.email: "email",
    EntityType.bearer_token: "bearer_token",
    EntityType.private_key: "private_key",
    EntityType.api_key: "api_key",
    EntityType.connection_string: "connection_string",
    EntityType.jwt: "jwt",
    EntityType.webhook_secret: "webhook_secret",
    EntityType.oauth_cloud_token: "oauth_cloud_token",
    EntityType.session_token: "session_token",
    EntityType.cloud_credential: "cloud_credential",
    EntityType.package_saas_token: "package_saas_token",
    EntityType.generic_secret: "generic_secret",
    EntityType.webhook_url: "webhook_url",
    EntityType.auth_header_token: "auth_header_token",
    EntityType.cloud_access_key_id: "cloud_access_key_id",
    EntityType.cloud_secret_key_assignment: "cloud_secret_key_assignment",
    EntityType.private_key_inline: "private_key_inline",
}


def build_placeholder(entity_type: EntityType, index: int) -> str:
    prefix = _PLACEHOLDER_PREFIX[entity_type]
    return f"@{prefix}{index}"
