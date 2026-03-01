import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
from src.preprocessing.resume_parser import ResumeParser


class FeaturePipeline:

    def __init__(self, max_features: int = 5000):
        self.parser = ResumeParser()
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            stop_words="english"
        )
        self.is_fitted = False

    def fit_transform(self, texts, experience_years):
        cleaned_texts = [self.parser.parse(t) for t in texts]

        text_features = self.vectorizer.fit_transform(cleaned_texts)

        numeric_features = pd.DataFrame({
            "experience_years": experience_years
        })

        final_features = hstack([text_features, numeric_features])

        self.is_fitted = True
        return final_features

    def transform(self, texts, experience_years):
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before transform.")

        cleaned_texts = [self.parser.parse(t) for t in texts]

        text_features = self.vectorizer.transform(cleaned_texts)

        numeric_features = pd.DataFrame({
            "experience_years": experience_years
        })

        final_features = hstack([text_features, numeric_features])

        return final_features

    def save(self, path: str):
        joblib.dump(self, path)

    @staticmethod
    def load(path: str):
        return joblib.load(path)