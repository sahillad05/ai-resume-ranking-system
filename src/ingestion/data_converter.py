import os
import pandas as pd


def convert_row_to_resume_text(row: pd.Series) -> str:
    """
    Convert structured CSV row into pseudo resume text.
    This ensures training data resembles real resume text.
    """

    skills = row["skills"]
    qualification = row["qualification"]
    experience = row["experience_level"]

    resume_text = (
        f"Candidate with skills: {skills}. "
        f"Qualification: {qualification}. "
        f"Experience level: {experience}."
    )

    return resume_text


def convert_csv_to_resume_text(input_path: str, output_path: str):
    """
    Reads structured CSV and converts it into
    text-based training dataset.
    """

    df = pd.read_csv(input_path)

    # Create pseudo resume text column
    df["resume_text"] = df.apply(convert_row_to_resume_text, axis=1)

    # Keep only necessary columns for training
    final_df = df[["candidate_id", "resume_text", "job_role"]]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)

    print("Conversion completed successfully.")
    print(f"Saved processed file at: {output_path}")
    print("\nSample Output:")
    print(final_df.head())


if __name__ == "__main__":
    INPUT_PATH = "data/raw/candidate_job_role_dataset.csv"
    OUTPUT_PATH = "data/processed/training_data.csv"

    convert_csv_to_resume_text(INPUT_PATH, OUTPUT_PATH)