# models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from config import engine  # <-- prends directement l'engine de config

# Crée toutes les tables
SQLModel.metadata.create_all(engine)

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    prenom: Optional[str] = Field(default=None, index=True)
    email: str = Field(index=True, unique=True)
    hashed_password: Optional[str] = None

    # Relation avec les emails
    emails: List["Email"] = Relationship(back_populates="user")


class Email(SQLModel, table=True):
    __tablename__ = "emails"

    id: Optional[int] = Field(default=None, primary_key=True)
    sujet: str = Field(index=True)        # sujet de l'email
    corps: str                             # contenu de l'email
    expediteur: str                         # expéditeur
    date_reception: datetime = Field(default_factory=datetime.utcnow)
    sentiment: Optional[str] = Field(default=None)  # positif, neutre, négatif

    # Clé étrangère vers User
    user_id: int = Field(foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="emails")
