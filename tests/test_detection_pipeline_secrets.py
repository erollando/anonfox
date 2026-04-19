from app.config.settings import get_settings
from app.detection.pipeline import DetectionPipeline
from app.replacement.pseudonymizer import TextPseudonymizer


def _pseudonymize(text: str, classes: list[str]) -> tuple[str, dict[str, str]]:
    pipeline = DetectionPipeline.default(get_settings())
    pseudonymizer = TextPseudonymizer()
    detections = pipeline.analyze(text=text, classes=classes, language="en")
    result = pseudonymizer.pseudonymize(text, detections)
    return result.text, result.mapping


def test_detect_jwt_and_replace() -> None:
    token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4iLCJpYXQiOjE1MTYyMzkwMjJ9."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    text, mapping = _pseudonymize(f"JWT={token}", ["jwt"])
    assert text == "JWT=@jwt1"
    assert mapping == {"@jwt1": token}


def test_detect_webhook_secret_and_replace() -> None:
    secret = "whsec_1234567890abcdefABCDEF12345678"
    text, mapping = _pseudonymize(f"WEBHOOK_SECRET={secret}", ["webhook_secret"])
    assert text == "WEBHOOK_SECRET=@webhook_secret1"
    assert mapping == {"@webhook_secret1": secret}


def test_jwt_alias_resolution() -> None:
    token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4iLCJpYXQiOjE1MTYyMzkwMjJ9."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    text, mapping = _pseudonymize(f"token={token}", ["json_web_token"])
    assert text == "token=@jwt1"
    assert mapping == {"@jwt1": token}


def test_webhook_secret_alias_resolution() -> None:
    secret = "whsec_abcdef0123456789abcdef01234567"
    text, mapping = _pseudonymize(f"secret={secret}", ["whsec"])
    assert text == "secret=@webhook_secret1"
    assert mapping == {"@webhook_secret1": secret}


def test_detect_vendor_api_key_and_replace() -> None:
    key = "ghp_1234567890abcdefghij1234567890ABCDEF"
    text, mapping = _pseudonymize(f"GITHUB_TOKEN={key}", ["api_key"])
    assert text == "GITHUB_TOKEN=@api_key1"
    assert mapping == {"@api_key1": key}


def test_detect_oauth_cloud_token_and_replace() -> None:
    token = "ya29.a0AfH6SMB4qFh2fRUP4M8d2Se7Xc9ABCD1234EFGH5678"
    text, mapping = _pseudonymize(f"google_oauth_token={token}", ["oauth_cloud_token"])
    assert text == "google_oauth_token=@oauth_cloud_token1"
    assert mapping == {"@oauth_cloud_token1": token}


def test_detect_bearer_token_and_replace() -> None:
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123def456ghi789.jkl012mno345pqr678"
    text, mapping = _pseudonymize(f"Authorization: Bearer {token}", ["bearer_token"])
    assert text == "Authorization: Bearer @bearer_token1"
    assert mapping == {"@bearer_token1": token}


def test_detect_session_cookie_token_and_replace() -> None:
    token = "vV5vYxWk0YfS1AqR9QpK3nLm2xZt8PdH"
    text, mapping = _pseudonymize(f"Set-Cookie: sessionid={token}; Path=/; HttpOnly", ["session_token"])
    assert text == "Set-Cookie: sessionid=@session_token1; Path=/; HttpOnly"
    assert mapping == {"@session_token1": token}


def test_detect_private_key_block_and_replace() -> None:
    key = (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASC...\n"
        "-----END PRIVATE KEY-----"
    )
    text, mapping = _pseudonymize(f"key:\n{key}\n", ["private_key"])
    assert text == "key:\n@private_key1\n"
    assert mapping == {"@private_key1": key}


def test_detect_connection_string_and_replace() -> None:
    dsn = "postgresql://db_user:supers3cret@db.example.com:5432/appdb?sslmode=require"
    text, mapping = _pseudonymize(f"DATABASE_URL={dsn}", ["connection_string"])
    assert text == "DATABASE_URL=@connection_string1"
    assert mapping == {"@connection_string1": dsn}


def test_detect_cloud_access_key_id_and_replace() -> None:
    key_id = "AKIA1234567890ABCDEF"
    text, mapping = _pseudonymize(f"aws_access_key_id={key_id}", ["cloud_access_key_id"])
    assert text == "aws_access_key_id=@cloud_access_key_id1"
    assert mapping == {"@cloud_access_key_id1": key_id}


def test_detect_cloud_secret_key_assignment_and_replace() -> None:
    secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    text, mapping = _pseudonymize(
        f"aws_secret_access_key={secret}",
        ["cloud_secret_key_assignment"],
    )
    assert text == "aws_secret_access_key=@cloud_secret_key_assignment1"
    assert mapping == {"@cloud_secret_key_assignment1": secret}


def test_detect_cloud_credential_and_replace() -> None:
    key_id = "ASIA1234567890ABCDEF"
    text, mapping = _pseudonymize(f"temporary_key={key_id}", ["cloud_credential"])
    assert text == "temporary_key=@cloud_credential1"
    assert mapping == {"@cloud_credential1": key_id}


def test_detect_package_saas_token_and_replace() -> None:
    token = "npm_1234567890abcdefghijklmnopqrstuvwxyz"
    text, mapping = _pseudonymize(f"NPM_TOKEN={token}", ["package_saas_token"])
    assert text == "NPM_TOKEN=@package_saas_token1"
    assert mapping == {"@package_saas_token1": token}


def test_detect_generic_high_entropy_secret_and_replace() -> None:
    secret = "Q4m7zX9kL2vP6tN8wR1yB3uH5sD7fJ9K"
    text, mapping = _pseudonymize(f"auth_secret={secret}", ["generic_secret"])
    assert text == "auth_secret=@generic_secret1"
    assert mapping == {"@generic_secret1": secret}


def test_ignore_generic_low_entropy_secret() -> None:
    text, mapping = _pseudonymize("auth_secret=changeme123", ["generic_secret"])
    assert text == "auth_secret=changeme123"
    assert mapping == {}


def test_detect_webhook_url_and_replace() -> None:
    url = "https://hooks.slack.com/services/T00000000/B00000000/abcdefghijklmnopqrstuvwxyz123456"
    text, mapping = _pseudonymize(f"SLACK_WEBHOOK={url}", ["webhook_url"])
    assert text == "SLACK_WEBHOOK=@webhook_url1"
    assert mapping == {"@webhook_url1": url}


def test_detect_auth_header_token_variant_and_replace() -> None:
    token = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    text, mapping = _pseudonymize(f"x-api-key: {token}", ["auth_header_token"])
    assert text == "x-api-key: @auth_header_token1"
    assert mapping == {"@auth_header_token1": token}


def test_detect_private_key_inline_and_replace() -> None:
    key = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tRUlORUxJTkVL"
    text, mapping = _pseudonymize(f"private_key={key}", ["private_key_inline"])
    assert text == "private_key=@private_key_inline1"
    assert mapping == {"@private_key_inline1": key}
