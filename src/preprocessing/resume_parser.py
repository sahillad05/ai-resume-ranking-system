import re
from typing import Dict


class ResumeParser:
    """
    Unified Resume Parser.
    Used for BOTH:
    - Training data (pseudo resume text)
    - PDF extracted resume text
    """

    def __init__(self):
        self.qualification_mapping = {
            "phd": 4,
            "master": 3,
            "bachelor": 2,
            "diploma": 1
        }

        self.experience_mapping = {
            "senior": 3,
            "mid": 2,
            "junior": 1
        }

    def clean_text(self, text: str) -> str:
        """
        Basic text cleaning.
        """
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_qualification_score(self, text: str) -> int:
        """
        Convert qualification into numeric score.
        """
        for key in self.qualification_mapping:
            if key in text:
                return self.qualification_mapping[key]
        return 0

    def extract_experience_score(self, text: str) -> int:
        """
        Convert experience level into numeric score.
        """
        for key in self.experience_mapping:
            if key in text:
                return self.experience_mapping[key]
        return 0

    def parse(self, text: str) -> Dict:
        """
        Main parsing method.
        Returns cleaned text + numeric features.
        """

        cleaned_text = self.clean_text(text)

        qualification_score = self.extract_qualification_score(cleaned_text)
        experience_score = self.extract_experience_score(cleaned_text)

        return {
            "cleaned_text": cleaned_text,
            "qualification_score": qualification_score,
            "experience_score": experience_score
        }