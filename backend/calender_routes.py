# app/api/calendar_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any

from config import get_session
from models import User
from calender_node import CalendarAddEventAction
from auth import get_current_user

router = APIRouter()

# Créer un événement dans le calendrier
@router.post("/add_event")
def add_event(
    email_content: str,   # contenu de l'email (texte brut ou extrait)
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        # Exemple de configuration de ton nœud
        configuration: Dict[str, Any] = {
            "calendar_provider": "google",  # ou "outlook"
            "title": "Événement extrait de l'email",
            "description": "Ajouté automatiquement depuis un email",
        }

        # Contexte contenant l'email
        context: Dict[str, Any] = {
            "email_content": email_content
        }

        # Exécuter le nœud
        node = CalendarAddEventAction()
        result = node.execute(configuration, context)

        return {
            "message": "Événement créé avec succès",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
