import pandas as pd
from feature_pipeline import FeaturePipeline

if __name__ == "__main__":

    data = pd.read_csv("data/processed/training_data.csv")

    pipeline = FeaturePipeline(max_features=100)

    X = pipeline.fit_transform(data["resume_text"])

    print("Feature shape:", X.shape)