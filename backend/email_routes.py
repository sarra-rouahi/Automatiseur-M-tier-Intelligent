# app/api/email_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from config import get_session
from models import Email, User
from auth import get_current_user # dépendance pour récupérer l'utilisateur connecté

router = APIRouter()

# ➤ Créer un email
@router.post("/", response_model=Email, status_code=status.HTTP_201_CREATED)
def create_email(email: Email, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Lier l'email à l'utilisateur connecté
    email.user_id = current_user.id
    db.add(email)
    db.commit()
    db.refresh(email)
    return email

# ➤ Lire tous les emails de l'utilisateur connecté
@router.get("/", response_model=List[Email])
def read_emails(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    emails = db.exec(select(Email).where(Email.user_id == current_user.id)).all()
    return emails

# ➤ Lire un email par ID
@router.get("/{email_id}", response_model=Email)
def read_email(email_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    email = db.get(Email, email_id)
    if not email or email.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    return email

# ➤ Mettre à jour un email
@router.put("/{email_id}", response_model=Email)
def update_email(email_id: int, updated_email: Email, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_email = db.get(Email, email_id)
    if not db_email or db_email.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    
    # Mise à jour champ par champ
    db_email.sujet = updated_email.sujet
    db_email.corps = updated_email.corps
    db_email.expediteur = updated_email.expediteur
    db_email.sentiment = updated_email.sentiment

    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

# ➤ Supprimer un email
@router.delete("/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_email = db.get(Email, email_id)
    if not db_email or db_email.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    
    db.delete(db_email)
    db.commit()
    return {"message": "Email supprimé avec succès"}
