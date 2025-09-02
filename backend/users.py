# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from config import get_session
from models import User
from user import UserCreate, UserUpdate, User as UserSchema  # Pydantic schemas
from auth import get_user_from_token  # sécurise via OAuth2 ou JWT

router = APIRouter(
)

# ➤ Créer un utilisateur
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_session)):
    # Vérifier si l'email existe déjà
    existing_user = db.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    db_user = User(
        nom=user.nom,
        prenom=user.prenom,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ➤ Récupérer tous les utilisateurs (avec pagination)
@router.get("/", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100,
               db: Session = Depends(get_session),
               current_user: User = Depends(get_user_from_token)):
    users = db.exec(select(User).offset(skip).limit(limit)).all()
    return users

# ➤ Récupérer un utilisateur par ID
@router.get("/{user_id}", response_model=UserSchema)
def read_user(user_id: int,
              db: Session = Depends(get_session),
              current_user: User = Depends(get_user_from_token)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_user

# ➤ Mettre à jour un utilisateur
@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user: UserUpdate,
                db: Session = Depends(get_session),
                current_user: User = Depends(get_user_from_token)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    update_data = user.dict(exclude_unset=True)

    # Vérifier si email mis à jour existe déjà chez un autre utilisateur
    if "email" in update_data:
        existing_user = db.exec(select(User).where(User.email == update_data["email"], User.id != user_id)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email déjà utilisé par un autre utilisateur")

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# ➤ Supprimer un utilisateur
@router.delete("/{user_id}")
def delete_user(user_id: int,
                db: Session = Depends(get_session),
                current_user: User = Depends(get_user_from_token)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(db_user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}
