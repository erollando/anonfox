from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "0.1.0"


def test_supported_classes() -> None:
    response = client.get("/supported-classes")
    assert response.status_code == 200
    payload = response.json()
    assert set(payload["classes"]) >= {
        "person",
        "phone",
        "email",
        "bearer_token",
        "private_key",
        "api_key",
        "connection_string",
        "jwt",
        "webhook_secret",
        "oauth_cloud_token",
        "session_token",
        "cloud_credential",
        "package_saas_token",
        "generic_secret",
        "webhook_url",
        "auth_header_token",
        "cloud_access_key_id",
        "cloud_secret_key_assignment",
        "private_key_inline",
    }


def test_pseudonymize_example_with_lowercase_name_and_phone() -> None:
    request_payload = {
        "text": "In this text, lowercased names are present. Mr pino daniele has told me his number is 01/2345678",
        "classes": ["person", "phone"],
        "language": "nl",
        "options": {
            "return_mapping": True,
            "include_detections": True,
            "person_mode": "full_span",
        },
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == (
        "In this text, lowercased names are present. @person1 has told me his number is @phone1"
    )
    assert payload["mapping"] == {
        "@person1": "Mr pino daniele",
        "@phone1": "01/2345678",
    }

    detections = payload["detections"]
    assert len(detections) == 2
    assert {item["entity_type"] for item in detections} == {"person", "phone"}


def test_selectable_classes_person_only() -> None:
    request_payload = {
        "text": "Mr pino daniele has phone number 01/2345678",
        "classes": ["person"],
        "language": "nl",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "@person1 has phone number 01/2345678"
    assert payload["mapping"] == {"@person1": "Mr pino daniele"}
    assert payload["detections"] is None


def test_repeated_value_reuses_placeholder() -> None:
    request_payload = {
        "text": "John Smith called John Smith on 01/2345678",
        "classes": ["person", "phone"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "@person1 called @person1 on @phone1"
    assert payload["mapping"] == {
        "@person1": "John Smith",
        "@phone1": "01/2345678",
    }


def test_depseudonymize_restores_text() -> None:
    request_payload = {
        "text": "@person1 has told me his number is @phone1",
        "mapping": {
            "@person1": "Mr pino daniele",
            "@phone1": "01/2345678",
        },
    }

    response = client.post("/depseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()
    assert payload["text"] == "Mr pino daniele has told me his number is 01/2345678"


def test_does_not_pseudonymize_told_as_person() -> None:
    request_payload = {
        "text": "Mr pino daniele told me his number is 01/2345678",
        "classes": ["person", "phone"],
        "language": "nl",
        "options": {"return_mapping": True, "include_detections": True},
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "@person1 told me his number is @phone1"
    assert payload["mapping"] == {
        "@person1": "Mr pino daniele",
        "@phone1": "01/2345678",
    }

    person_detections = [
        detection for detection in payload["detections"] if detection["entity_type"] == "person"
    ]
    assert len(person_detections) == 1
    assert person_detections[0]["text"] == "Mr pino daniele"


def test_pseudonymize_bearer_token() -> None:
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123def456ghi789.jkl012mno345pqr678"
    request_payload = {
        "text": f"Authorization: Bearer {token}",
        "classes": ["bearer_token"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "Authorization: Bearer @bearer_token1"
    assert payload["mapping"] == {"@bearer_token1": token}


def test_pseudonymize_private_key_block() -> None:
    private_key = (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASC...\n"
        "-----END PRIVATE KEY-----"
    )
    request_payload = {
        "text": f"secrets:\n{private_key}\n",
        "classes": ["private_key"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "secrets:\n@private_key1\n"
    assert payload["mapping"] == {"@private_key1": private_key}


def test_pseudonymize_vendor_api_key() -> None:
    key = "ghp_1234567890abcdefghij1234567890ABCDEF"
    request_payload = {
        "text": f"export GITHUB_TOKEN={key}",
        "classes": ["api_key"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "export GITHUB_TOKEN=@api_key1"
    assert payload["mapping"] == {"@api_key1": key}


def test_pseudonymize_connection_string() -> None:
    dsn = "postgresql://db_user:supers3cret@db.example.com:5432/appdb?sslmode=require"
    request_payload = {
        "text": f"DATABASE_URL={dsn}",
        "classes": ["connection_string"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "DATABASE_URL=@connection_string1"
    assert payload["mapping"] == {"@connection_string1": dsn}


def test_class_aliases_for_new_secret_recognizers() -> None:
    request_payload = {
        "text": "Authorization: Bearer abcdefghijklmnop123456",
        "classes": ["bearer", "apikey", "dsn"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200


def test_pseudonymize_jwt() -> None:
    token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4iLCJpYXQiOjE1MTYyMzkwMjJ9."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    request_payload = {
        "text": f"token={token}",
        "classes": ["jwt"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "token=@jwt1"
    assert payload["mapping"] == {"@jwt1": token}


def test_pseudonymize_webhook_secret() -> None:
    secret = "whsec_1234567890abcdefABCDEF12345678"
    request_payload = {
        "text": f"STRIPE_WEBHOOK_SECRET={secret}",
        "classes": ["webhook_secret"],
        "language": "en",
    }

    response = client.post("/pseudonymize", json=request_payload)
    assert response.status_code == 200
    payload = response.json()

    assert payload["text"] == "STRIPE_WEBHOOK_SECRET=@webhook_secret1"
    assert payload["mapping"] == {"@webhook_secret1": secret}
