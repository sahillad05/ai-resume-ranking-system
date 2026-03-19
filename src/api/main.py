import joblib
import PyPDF2
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

app = FastAPI(title="AI Resume Classification API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.preprocessing.feature_pipeline import FeaturePipeline
from src.models.ranker import AdvancedResumeRanker

# Load artifacts
pipeline = FeaturePipeline.load("artifacts/feature_pipeline.pkl")
model = joblib.load("artifacts/model.pkl")
label_encoder = joblib.load("artifacts/label_encoder.pkl")
ranker = AdvancedResumeRanker()

from pathlib import Path

# Mount frontend directory for static assets
FRONTEND_DIR = str(Path(__file__).resolve().parent.parent.parent / "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")


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
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"AI Resume Classification API is running (Frontend not found at {index_path})"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


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
            "final_score": round(result["final_score"] * 100, 2),
            "similarity": round(result["similarity"] * 100, 2),
            "classification_confidence": round(result["classification_confidence"] * 100, 2),
            "experience_years": result["experience_years"]
        }
        for result in ranking_results
    ]

    return {
        "job_description": job_description,
        "ranking": ranked_output
    }