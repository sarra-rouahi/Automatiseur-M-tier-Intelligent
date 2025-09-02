# app/api/sentiment.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import pipeline

# Définition du router
router = APIRouter()

# Initialiser le pipeline Hugging Face (sentiment analysis)
# Le modèle "distilbert-base-uncased-finetuned-sst-2-english" est léger et rapide
sentiment_analyzer = pipeline("sentiment-analysis")

# Schéma pour la requête
class SentimentRequest(BaseModel):
    text: str

# Endpoint pour analyser le sentiment d'un texte
@router.post("/")
def analyze_sentiment(request: SentimentRequest):
    if not request.text or request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Texte vide non autorisé")

    try:
        result = sentiment_analyzer(request.text)[0]  # Ex : {'label': 'POSITIVE', 'score': 0.99}
        return {
            "text": request.text,
            "sentiment": result["label"],
            "confidence": round(result["score"], 3)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse : {str(e)}")
