# app/api/calendar_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from auth import get_current_user
from models import User
from calender_node import CalendarAddEventAction  # fichier contenant ta classe

router = APIRouter()

# Modèle pour la requête POST
class CalendarRequest(BaseModel):
    email_content: str
    configuration: Dict[str, Any] = {}

# Endpoint pour créer un événement
@router.post("/add_event", summary="Ajouter un événement au calendrier")
def add_event(
    payload: CalendarRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        node = CalendarAddEventAction()
        context = {
            "email_data": {
                "subject": payload.email_content,
                "body": payload.email_content
            },
            "category": "rdv"  # simuler que l'email est classifié comme RDV
        }
        result = node.execute(configuration=payload.configuration, context=context)
        return {"message": "Événement créé", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
