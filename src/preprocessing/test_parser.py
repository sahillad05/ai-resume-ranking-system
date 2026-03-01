from resume_parser import ResumeParser

if __name__ == "__main__":
    parser = ResumeParser()

    sample_text = "Candidate with skills: Python, SQL. Qualification: Master's. Experience level: Senior."

    result = parser.parse(sample_text)

    print(result)