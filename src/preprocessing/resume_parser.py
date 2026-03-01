import re


class ResumeParser:
    """
    Clean resume text for NLP training.
    Used for BOTH:
    - Training (resume_text column)
    - PDF inference
    """

    def clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def parse(self, text: str) -> str:
        return self.clean_text(text)