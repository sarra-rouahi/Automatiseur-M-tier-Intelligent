# ocr.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ocr import OCRImageAction  # ton fichier contenant la classe OCRImageAction

router = APIRouter()

# Définir les modèles pour FastAPI
class Attachment(BaseModel):
    filename: str
    content_type: str
    data: str  # base64 de l'image

class OCRRequest(BaseModel):
    configuration: Optional[Dict[str, Any]] = {}
    context: Dict[str, Any]

# Route pour tester l'OCR
@router.post("/extract-text", summary="Extraire le texte des images")
def extract_text(payload: OCRRequest):
    ocr_node = OCRImageAction()
    try:
        result = ocr_node.execute(configuration=payload.configuration, context=payload.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OCR: {str(e)}")
