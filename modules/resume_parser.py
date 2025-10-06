# modules/resume_parser.py
import pdfplumber
from docx import Document
import os

def extract_text(file_path: str) -> str:
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError("Unsupported file format: only PDF or DOCX allowed")

    return text.strip()

import re
import spacy

# Attempt to load spaCy model, auto-install if missing; fall back to blank pipeline
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    try:
        from spacy.cli import download as spacy_download
        spacy_download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        # Fallback: blank English pipeline (NER unavailable, but tokenization works)
        nlp = spacy.blank("en")

def extract_basic_info(text: str) -> dict:
    doc = nlp(text)

    # --- Email & Phone ---
    email = re.search(r"\b[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    phone = re.search(r"(\+?\d[\d -]{8,}\d)", text)

    # --- Name (first NER entity of type PERSON) ---
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)

    # --- Education keywords ---
    education_keywords = ["B.Tech", "M.Tech", "B.Sc", "M.Sc", "MBA", "PhD", "Bachelor", "Master"]
    education = next((word for word in education_keywords if word.lower() in text.lower()), None)

    return {
        "name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "education": education
    }

COMMON_SKILLS = [
    "python", "sql", "aws", "docker", "javascript", "flask", "django",
    "react", "excel", "tableau", "machine learning", "linux", "git", "langchain"
]

def extract_skills(text: str) -> list:
    skills_found = []
    for skill in COMMON_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.I):
            skills_found.append(skill.title())
    return skills_found

import json
from datetime import datetime

def parse_resume(file_path: str, output_path: str = "output/parsed_resume.json"):
    text = extract_text(file_path)
    basic = extract_basic_info(text)
    skills = extract_skills(text)

    resume_data = {
        **basic,
        "skills": skills,
        "extracted_at": datetime.now().isoformat()
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resume_data, f, indent=4)

    print("✅ Resume parsed successfully!")
    return resume_data

