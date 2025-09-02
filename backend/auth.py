# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session, select
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
import requests

from config import get_session
from models import User
from pydantic import BaseModel
# --- Config JWT ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret_jwt_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Router ---
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
class RegisterRequest(BaseModel):
    email: str
    password: str
    nom: str | None = ""
    prenom: str | None = ""
class LoginRequest(BaseModel):
    email: str
    password: str
# --- Utils ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def get_user_by_email(email: str, db: Session):
    return db.exec(select(User).where(User.email == email)).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

# --- Routes ---

# Inscription locale
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest, db: Session = Depends(get_session)
):
    if get_user_by_email(payload.email, db):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    if not payload.password:
        raise HTTPException(status_code=400, detail="Le mot de passe est obligatoire")

    user = User(
        email=payload.email,
        nom=payload.nom or "Unknown",
        prenom=payload.prenom or "",
        hashed_password=hash_password(payload.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'utilisateur : {str(e)}")

    return {"message": "Utilisateur créé avec succès", "email": user.email}

# Connexion locale (email + mot de passe)
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_session)):
    user = get_user_by_email(payload.email, db)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
# Connexion via Google OAuth2 (frontend envoie id_token)
@router.post("/login/google")
async def login_google(request: Request, db: Session = Depends(get_session)):
    body =  await request.json()
    id_token = body.get("id_token")

    if not id_token:
        raise HTTPException(status_code=400, detail="id_token manquant")

    # Vérifier le token avec Google
    google_resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
    if google_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Token Google invalide")

    data = google_resp.json()
    email = data.get("email")
    nom = data.get("family_name", "")
    prenom = data.get("given_name", "")

    # Créer ou récupérer l’utilisateur
    user = get_user_by_email(email, db)
    if not user:
        user = User(email=email, nom=nom, prenom=prenom, hashed_password="")
        db.add(user)
        db.commit()
        db.refresh(user)

    # Générer un JWT interne
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Profil utilisateur (protégé)
@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "email": current_user.email
    }
