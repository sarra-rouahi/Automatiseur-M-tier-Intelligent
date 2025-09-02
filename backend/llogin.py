# app/api/auth_local.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os

from config import get_session
from models import User

# --- Config JWT ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret_jwt_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Router ---
router = APIRouter(prefix="/auth_local", tags=["auth_local"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth_local/login")

# --- Fonctions utilitaires ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

# Inscription
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(email: str, password: str, nom: str = "", prenom: str = "", db: Session = Depends(get_session)):
    if get_user_by_email(email, db):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    user = User(
        email=email,
        nom=nom or "Unknown",
        prenom=prenom or "",
        hashed_password=hash_password(password)  # champ hashed_password à ajouter dans User
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Utilisateur créé avec succès", "email": user.email}

# Login
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Récupérer l'utilisateur connecté
@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"nom": current_user.nom, "prenom": current_user.prenom, "email": current_user.email}
