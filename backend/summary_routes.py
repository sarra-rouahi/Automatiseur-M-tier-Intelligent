# app/api/summary_routes.py
import os
import re
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

router = APIRouter()

# -------- Config modèle --------
DEFAULT_MODEL_ID = os.getenv("HF_SUMM_MODEL", "csebuetnlp/mT5_multilingual_XLSum")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "4000"))

summarizer = None
model_id_loaded = None

# -------- Schémas --------
class EmailIn(BaseModel):
    subject: Optional[str] = Field(None, description="Objet de l'email")
    body: str = Field(..., description="Corps de l'email")
    lang: Optional[str] = Field(None, description="Code langue indicatif")
    min_length: int = Field(25, ge=5, le=400)
    max_length: int = Field(150, ge=30, le=1000)

class SummaryOut(BaseModel):
    summary: str
    model_id: str
    input_chars: int
    min_length: int
    max_length: int
    trimmed: bool

# -------- Utils --------
TAG_RE = re.compile(r"<[^>]+>")
def strip_html(text: str) -> str:
    return TAG_RE.sub("", text)

def build_input_text(subject: Optional[str], body: str, model_id: str, lang: Optional[str]) -> str:
    body_clean = strip_html(body).strip()
    subj = (subject or "").strip()
    combined = f"{subj}. {body_clean}" if subj else body_clean
    if "t5" in model_id.lower():
        return "summarize: " + combined
    return combined

# -------- Lifecycle router --------
@router.on_event("startup")
def load_model():
    global summarizer, model_id_loaded
    if summarizer is None:
        tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL_ID)
        model = AutoModelForSeq2SeqLM.from_pretrained(DEFAULT_MODEL_ID)
        summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
        model_id_loaded = DEFAULT_MODEL_ID

# -------- Routes --------
@router.get("/", summary="Status du résumé")
def root():
    return {"status": "ok", "model_id": model_id_loaded}

@router.post("/summarize-email", response_model=SummaryOut, summary="Résumé automatique d'email")
def summarize_email(payload: EmailIn):
    if summarizer is None:
        raise HTTPException(status_code=500, detail="Modèle non initialisé")

    text = build_input_text(payload.subject, payload.body, model_id_loaded, payload.lang)
    trimmed = False
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS]
        trimmed = True

    min_len = min(max(payload.min_length, 5), payload.max_length - 1)
    max_len = payload.max_length

    try:
        result = summarizer(text, min_length=min_len, max_length=max_len, do_sample=False)
        summary_text = result[0]["summary_text"].strip()
        return SummaryOut(
            summary=summary_text,
            model_id=model_id_loaded,
            input_chars=len(text),
            min_length=min_len,
            max_length=max_len,
            trimmed=trimmed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de résumé: {e}")
