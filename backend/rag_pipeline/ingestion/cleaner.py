import re

class DataCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        # text = text.lower() # Commenting out to preserve headers and case-sensitivity for format logic
        # Remove special characters but keep punctuation and newlines
        text = re.sub(r'[^\w\s\.\,\!\?\-\#\:]', '', text)
        # Normalize horizontal whitespace only
        text = re.sub(r'[ \t]+', ' ', text).strip()
        # Remove headers/ads placeholder (example logic)
        text = re.sub(r'---.*?---', '', text)
        return text
