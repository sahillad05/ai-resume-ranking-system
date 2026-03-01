import pandas as pd


def clean_resume_dataset(input_path: str, output_path: str):
    rows = []

    with open(input_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()

            # Remove outer quotes
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]

            rows.append(line)

    # First row = header
    header = rows[0].split(",", 4)

    data = []
    for row in rows[1:]:
        parts = row.split(",", 4)
        if len(parts) == 5:
            data.append(parts)

    df = pd.DataFrame(data, columns=header)

    # Clean column names
    df.columns = [col.strip() for col in df.columns]

    # Convert experience_years to numeric
    df["experience_years"] = pd.to_numeric(
        df["experience_years"],
        errors="coerce"
    ).fillna(0)

    df.to_csv(output_path, index=False)

    print("Dataset cleaned successfully.")
    print("Columns:", df.columns.tolist())
    print("Unique categories sample:", df["category"].unique()[:10])


if __name__ == "__main__":
    clean_resume_dataset(
        "data/raw/resume.csv",
        "data/raw/resume_cleaned.csv"
    )