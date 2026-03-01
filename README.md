# AI Resume Screening & Candidate Ranking System

## Overview

This project builds a unified AI-based Resume Screening and Candidate Ranking system.

Core principle:
Training and inference pipelines are IDENTICAL to avoid feature mismatch.

## Architecture

Structured CSV Dataset
→ Convert to pseudo resume text
→ Unified Resume Parser
→ TF-IDF + Numeric Feature Pipeline
→ XGBoost Classifier
→ FastAPI Backend
→ Streamlit UI

## Tech Stack

- Python
- Scikit-learn
- XGBoost
- FastAPI
- Streamlit
- PyPDF2

## Project Structure

ai-resume-ranking-system/
│
├── data/
│   ├── raw/
│
├── src/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── models/
│   ├── api/
│   ├── utils/
│
├── streamlit_app/
│
├── requirements.txt
├── .gitignore
├── README.md

## Environment Setup

Create conda environment:

conda create -n resume-ranking python=3.10
conda activate resume-ranking

Install dependencies:

pip install -r requirements.txt