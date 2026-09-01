"""
Configuração do banco de dados.

Usa SQLite por padrão (arquivo local, zero configuração) para o protótipo.
Para produção, basta trocar DATABASE_URL por Postgres/MySQL — o restante do
código (SQLAlchemy ORM) não muda.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alocacao.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
