import logging
from deep_translator import GoogleTranslator


def translate_to_english(text: str) -> str:
    """
    Translate arbitrary text to English. Falls back to the original text on failure.
    """
    if not text:
        return text

    try:
        translator = GoogleTranslator(source="auto", target="en")
        translation = translator.translate(text)
        logging.debug("Original: %s | Translated: %s", text, translation)
        return translation
    except Exception as exc:  # pragma: no cover - defensive logging
        logging.error("Error translating text: %s", exc)
        return text

