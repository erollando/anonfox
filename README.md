# anonfox

Reversible pseudonymization service for Dutch and English text, built with FastAPI.

## What it does

- Detects selected PII and secret classes in text:
  - PII: `person`, `phone`, `email`
  - Secrets:
    - `jwt`, `api_key`, `webhook_secret`, `oauth_cloud_token`, `bearer_token`
    - `session_token`, `private_key`, `private_key_inline`, `connection_string`
    - `cloud_credential`, `cloud_access_key_id`, `cloud_secret_key_assignment`
    - `package_saas_token`, `generic_secret`, `webhook_url`, `auth_header_token`
- Replaces detections with deterministic placeholders (`@person1`, `@phone1`, ...)
- Returns explicit mapping for reversible pseudonymization
- Supports de-pseudonymization using the mapping object
- Uses a hybrid detection pipeline:
  - Regex recognizers for structured entities (phone, email)
  - Heuristic recognizer for person entities with lowercase-aware logic
  - Optional spaCy NER provider for person detection
  - Pattern-based recognizers for developer secrets (tokens, key blocks, DSNs)

`person_mode` currently defaults to and behaves as `full_span`. `split_name` is reserved for a future extension.

## API

- `GET /health`
- `GET /supported-classes`
- `POST /pseudonymize`
- `POST /depseudonymize`

### `POST /pseudonymize` request

```json
{
  "text": "Mr pino daniele has told me his number is 01/2345678",
  "classes": ["person", "phone"],
  "language": "nl",
  "options": {
    "return_mapping": true,
    "include_detections": true,
    "person_mode": "full_span"
  }
}
```

### `POST /pseudonymize` response

```json
{
  "text": "@person1 has told me his number is @phone1",
  "mapping": {
    "@person1": "Mr pino daniele",
    "@phone1": "01/2345678"
  },
  "detections": [
    {
      "entity_type": "person",
      "text": "Mr pino daniele",
      "start": 0,
      "end": 15,
      "confidence": 0.98,
      "source": "hybrid_person_recognizer",
      "placeholder": "@person1"
    },
    {
      "entity_type": "phone",
      "text": "01/2345678",
      "start": 40,
      "end": 50,
      "confidence": 0.999,
      "source": "phone_regex_recognizer",
      "placeholder": "@phone1"
    }
  ]
}
```

### `POST /depseudonymize` request

```json
{
  "text": "@person1 has told me his number is @phone1",
  "mapping": {
    "@person1": "Mr pino daniele",
    "@phone1": "01/2345678"
  }
}
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Optional spaCy NER

spaCy is included in `requirements.txt`. Install the language models and enable spaCy NER:

```bash
python -m spacy download en_core_web_sm
python -m spacy download nl_core_news_sm
export ANONFOX_ENABLE_SPACY_NER=true
```

## Tests

```bash
pytest
```
