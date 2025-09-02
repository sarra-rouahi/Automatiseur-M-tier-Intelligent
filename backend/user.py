# app/api/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from config import get_session
from models import User

router = APIRouter()

# Créer un utilisateur
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: Session = Depends(get_session)):
    # Vérifier si l’email existe déjà
    existing_user = db.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Lire tous les utilisateurs
@router.get("/", response_model=List[User])
def read_users(db: Session = Depends(get_session)):
    users = db.exec(select(User)).all()
    return users

# Lire un utilisateur par ID
@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# Mettre à jour un utilisateur
@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Mise à jour champ par champ
    db_user.nom = updated_user.nom
    db_user.prenom = updated_user.prenom
    db_user.email = updated_user.email

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Supprimer un utilisateur
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(db_user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}
# app/api/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
import re

from config import get_session
from models import User

router = APIRouter(prefix="/users", tags=["users"])

# --- Fonction utilitaire pour validation email ---
def validate_email(email: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        raise HTTPException(status_code=400, detail="Email invalide")

# --- Créer un utilisateur ---
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: Session = Depends(get_session)):
    validate_email(user.email)
    
    existing_user = db.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- Lire tous les utilisateurs ---
@router.get("/", response_model=List[User])
def read_users(db: Session = Depends(get_session)):
    users = db.exec(select(User)).all()
    return users

# --- Lire un utilisateur par ID ---
@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# --- Mettre à jour un utilisateur ---
@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    validate_email(updated_user.email)

    # Vérifier que l’email n’est pas déjà utilisé par un autre utilisateur
    existing_user = db.exec(
        select(User).where(User.email == updated_user.email, User.id != user_id)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé par un autre utilisateur")

    # Mise à jour champ par champ
    db_user.nom = updated_user.nom
    db_user.prenom = updated_user.prenom
    db_user.email = updated_user.email

    db.commit()
    db.refresh(db_user)
    return db_user

# --- Supprimer un utilisateur ---
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(db_user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}
