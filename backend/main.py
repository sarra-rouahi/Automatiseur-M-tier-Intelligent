# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import create_db_and_tables
# Importer tes routes
import user
import email_routes as email
import ocr_routes as ocr 
import sentiment
import summary_routes
import trig_routes
import calender_routes
import auth as auth 
import classifier_routes
# Créer l'application FastAPI
app = FastAPI(
    title="Automatiseur Métier Intelligent",
    description="API centralisant Users, Emails, OCR, Sentiment, Résumé, Triggers",
    version="1.0.0"
)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
# Configurer CORS (optionnel mais utile si tu appelles depuis React/Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu peux limiter aux domaines de confiance
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers si tu les as définis avec APIRouter
# Exemple dans user.py tu devrais avoir `router = APIRouter()`
try:
    app.include_router(user.router , prefix="/users", tags=["Utilisateurs"])
except:
    print("⚠️ Pas de router trouvé dans user.py")
try:
    app.include_router(calender_routes.router , prefix="/calendar", tags=["Calendrier"])
except:
    print("⚠️ Pas de router trouvé dans calendar_routes.py")
try:
    app.include_router(auth.router, prefix="/auth", tags=["Authentification"])
except:
    print("⚠️ Pas de router trouvé dans auth.py")
try:
    app.include_router(email.router , prefix="/emails", tags=["Emails"])
except:
    print("⚠️ Pas de router trouvé dans email.py")

try:
    app.include_router(ocr.router , prefix="/ocr", tags=["OCR"])
except:
    print("⚠️ Pas de router trouvé dans ocr.py")

try:
    app.include_router(sentiment.router , prefix="/sentiment", tags=["Analyse de sentiment"])
except:
    print("⚠️ Pas de router trouvé dans sentiment.py")

try:
    app.include_router(summary_routes.router , prefix="/summary", tags=["Résumé de texte"])
except:
    print("⚠️ Pas de router trouvé dans summary_routes.py")
try:
    app.include_router(trig_routes.router   , prefix="/triggers", tags=["Triggers"])
except:
    print("⚠️ Pas de router trouvé dans trigemail.py")
try:
    app.include_router(classifier_routes.router, prefix="/classifier", tags=["Classification de texte"])
except:
    print("⚠️ Pas de router trouvé dans classifier_routes.py")
# Route de test
@app.get("/")
def root():
    return {"message": "🚀 API Automatiseur Métier Intelligent démarrée avec succès !"}

