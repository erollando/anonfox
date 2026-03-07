# AGENTS.md

## Project
Reversible FastAPI pseudonymization service for Dutch and English text.

This repository implements a hybrid PII pseudonymization API with reversible mappings.
The primary classes are PERSON and PHONE.
The service pseudonymizes text into typed placeholders and can restore the original text from an explicit mapping.

This is not an anonymization-only system and not a crypto-first system.

---

## Core objective

Build a clean, testable Python/FastAPI service that:

- detects selected PII classes in input text
- pseudonymizes them into stable typed placeholders
- returns optional detection metadata
- supports de-pseudonymization using explicit mappings
- works for English and Dutch
- handles lowercase names as an important requirement
- uses a hybrid detection approach

---

## Product boundary

### In scope
- FastAPI service
- request/response schemas
- person and phone detection first
- hybrid detection pipeline
- deterministic placeholder replacement
- reversible mapping output
- de-pseudonymization
- tests
- clear README

### Out of scope for v1
- keyed crypto as the primary design
- irreversible anonymization pipeline
- OCR
- PDF/image processing
- browser UI
- database-heavy architecture unless clearly justified
- universal split of name vs surname as the default mode

---

## Design principles

1. Hybrid detection first
   - Combine rule-based and NLP-based approaches.
   - Use regex/pattern logic for structured PII such as phones.
   - Use NER and heuristics for person entities.
   - Keep recognizers modular and composable.

2. Reversible pseudonymization
   - The transformed text alone is not enough to restore originals.
   - Reversal depends on an explicit mapping object or equivalent explicit state.
   - Never pretend placeholders are self-decoding.

3. Full-span person replacement by default
   - Prefer @person1 over @name1 + @surname1.
   - Add split-name support only as an optional later feature.
   - Do not force structure that detection cannot reliably justify.

4. Deterministic behavior
   - Placeholder assignment must be stable within a request.
   - Overlap resolution must be deterministic.
   - Round-trip replacement and reversal must be testable.

5. Simple service shape
   - Build a solid API and internal architecture.
   - Do not overengineer infrastructure in v1.

---

## Preferred stack

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- Pytest
- A modular recognizer framework, preferably Presidio-centered or equivalent
- spaCy and/or other NLP components where helpful

Keep heavy model assumptions behind clear interfaces.
Do not hard-wire the whole design to one NER backend if it can be avoided.

---

## Target architecture

The code should generally converge toward a structure like:

`text
app/
  api/
    routes_health.py
    routes_pseudonymize.py
    routes_depseudonymize.py
    routes_supported_classes.py
  schemas/
    requests.py
    responses.py
    common.py
  detection/
    pipeline.py
    registry.py
    types.py
    overlap.py
    language.py
  recognizers/
    phone.py
    person.py
    email.py
    base.py
  replacement/
    placeholders.py
    pseudonymizer.py
  reversal/
    depseudonymizer.py
  config/
    settings.py
  main.py
tests/
README.md
AGENTS.md
pyproject.toml
