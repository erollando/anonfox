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
    assert set(payload["classes"]) >= {"person", "phone", "email"}


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
