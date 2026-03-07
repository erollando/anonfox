SUPPORTED_LANGUAGES = {"en", "nl"}


def normalize_language(language: str) -> str:
    normalized = language.strip().lower()
    if normalized not in SUPPORTED_LANGUAGES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise ValueError(f"Unsupported language '{language}'. Supported languages: {supported}")
    return normalized
