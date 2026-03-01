import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
from resume_parser import ResumeParser


class FeaturePipeline:
    """
    Unified feature pipeline for BOTH:
    - Training
    - Inference
    """

    def __init__(self, max_features: int = 500):
        self.parser = ResumeParser()
        self.vectorizer = TfidfVectorizer(max_features=max_features)
        self.is_fitted = False

    def fit_transform(self, texts):
        """
        Used during training.
        """

        cleaned_texts = []
        qualification_scores = []
        experience_scores = []

        for text in texts:
            parsed = self.parser.parse(text)

            cleaned_texts.append(parsed["cleaned_text"])
            qualification_scores.append(parsed["qualification_score"])
            experience_scores.append(parsed["experience_score"])

        # TF-IDF text features
        text_features = self.vectorizer.fit_transform(cleaned_texts)

        # Numeric features
        numeric_features = pd.DataFrame({
            "qualification_score": qualification_scores,
            "experience_score": experience_scores
        })

        final_features = hstack([text_features, numeric_features])

        self.is_fitted = True

        return final_features

    def transform(self, texts):
        """
        Used during inference.
        """

        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before calling transform.")

        cleaned_texts = []
        qualification_scores = []
        experience_scores = []

        for text in texts:
            parsed = self.parser.parse(text)

            cleaned_texts.append(parsed["cleaned_text"])
            qualification_scores.append(parsed["qualification_score"])
            experience_scores.append(parsed["experience_score"])

        text_features = self.vectorizer.transform(cleaned_texts)

        numeric_features = pd.DataFrame({
            "qualification_score": qualification_scores,
            "experience_score": experience_scores
        })

        final_features = hstack([text_features, numeric_features])

        return final_features

    def save(self, path: str):
        joblib.dump(self, path)

    @staticmethod
    def load(path: str):
        return joblib.load(path)