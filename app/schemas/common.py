from enum import Enum


class LanguageCode(str, Enum):
    en = "en"
    nl = "nl"


class PersonMode(str, Enum):
    full_span = "full_span"
    split_name = "split_name"
