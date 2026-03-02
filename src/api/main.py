import joblib
import PyPDF2
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from src.preprocessing.feature_pipeline import FeaturePipeline

app = FastAPI(title="AI Resume Classification API")

# Load artifacts
pipeline = FeaturePipeline.load("artifacts/feature_pipeline.pkl")
model = joblib.load("artifacts/model.pkl")
label_encoder = joblib.load("artifacts/label_encoder.pkl")


def extract_text_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + " "

    return text.strip()


@app.get("/")
def home():
    return {"message": "AI Resume Classification API is running"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF files are supported"}
        )

    pdf_text = extract_text_from_pdf(file.file)

    if not pdf_text:
        return JSONResponse(
            status_code=400,
            content={"error": "Could not extract text from PDF"}
        )

    # Default experience for inference
    experience_years = [0]

    features = pipeline.transform(
        [pdf_text],
        experience_years
    )

    probabilities = model.predict_proba(features)[0]
    predicted_index = probabilities.argmax()
    predicted_role = label_encoder.inverse_transform([predicted_index])[0]
    confidence = float(probabilities[predicted_index])

    return {
        "predicted_category": predicted_role,
        "confidence": round(confidence, 4)
    }


from src.models.ranker import ResumeRanker
from typing import List
from fastapi import Form

ranker = ResumeRanker()


@app.post("/rank")
async def rank_resumes(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):

    resume_texts = []
    file_names = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            continue

        text = extract_text_from_pdf(file.file)

        if text:
            resume_texts.append(text)
            file_names.append(file.filename)

    if not resume_texts:
        return {"error": "No valid resume text extracted"}

    ranking_results = ranker.rank_resumes(
        job_description,
        resume_texts
    )

    ranked_output = [
        {
            "file_name": file_names[result["resume_index"]],
            "score": round(result["score"], 4)
        }
        for result in ranking_results
    ]

    return {
        "job_description": job_description,
        "ranking": ranked_output
    }