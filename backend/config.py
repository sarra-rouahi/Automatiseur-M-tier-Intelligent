from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine

# URL PostgreSQL
postgres_url = "postgresql://sarra:tonton@localhost:5432/automatiseur"

# Création du moteur sans connect_args
engine = create_engine(postgres_url, echo=True)  # echo=True pour debug

def create_db_and_tables():
    """Créer toutes les tables définies par SQLModel"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dépendance pour obtenir une session de DB"""
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
