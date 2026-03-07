import re


class TextDepseudonymizer:
    def depseudonymize(self, text: str, mapping: dict[str, str]) -> str:
        if not mapping:
            return text

        pattern = re.compile("|".join(re.escape(key) for key in sorted(mapping, key=len, reverse=True)))
        return pattern.sub(lambda match: mapping[match.group(0)], text)
