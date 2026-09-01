from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Sector(Base):
    __tablename__ = "sectors"
    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    coordenador = Column(String, nullable=False)

    teams = relationship("Team", back_populates="sector")


class Room(Base):
    __tablename__ = "rooms"
    id = Column(String, primary_key=True)
    andar = Column(Integer, nullable=False)
    capacidade = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    recursos = Column(JSON, default=list)  # ex: ["projetor", "tv"]
    acessivel = Column(Boolean, default=False)
    disponivel = Column(Boolean, default=True)


class Team(Base):
    __tablename__ = "teams"
    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    setor_id = Column(String, ForeignKey("sectors.id"), nullable=False)
    tamanho = Column(Integer, nullable=False)
    prioridade = Column(String, nullable=False, default="media")  # alta | media | baixa
    grupo_proximidade = Column(String, nullable=True)
    req_equip = Column(JSON, nullable=True)  # ex: ["computadores"]

    sector = relationship("Sector", back_populates="teams")


class Constraint(Base):
    __tablename__ = "constraints"
    id = Column(String, primary_key=True)
    ativa = Column(Boolean, default=True)
    tipo = Column(String, nullable=False)
    alvo = Column(String, nullable=True)  # team_id ou setor_id, dependendo do tipo
    valor = Column(JSON, nullable=True)
    descricao = Column(String, nullable=False)


class AllocationRun(Base):
    __tablename__ = "allocation_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String, default="coordenador-geral")
    algoritmo = Column(String, default="allocation-engine-v1")
    equipes_analisadas = Column(Integer)
    salas_analisadas = Column(Integer)
    equipes_alocadas = Column(Integer)
    equipes_nao_alocadas = Column(Integer)
    violacoes = Column(Integer)
    ocupacao_prevista = Column(Float)
    tempo_ms = Column(Float)

    results = relationship("AllocationResult", back_populates="run", cascade="all, delete-orphan")
    exceptions = relationship("AllocationException", back_populates="run", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="run", cascade="all, delete-orphan")


class AllocationResult(Base):
    __tablename__ = "allocation_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("allocation_runs.id"))
    team_id = Column(String)
    team_name = Column(String)
    setor_id = Column(String)
    tamanho = Column(Integer)
    sala_id = Column(String)
    andar = Column(Integer)
    capacidade = Column(Integer)
    ocupacao = Column(Float)
    alternatives_evaluated = Column(Integer)
    status = Column(String, default="aceita")  # aceita | rejeitada | alterada

    run = relationship("AllocationRun", back_populates="results")


class AllocationException(Base):
    __tablename__ = "allocation_exceptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("allocation_runs.id"))
    team_id = Column(String)
    team_name = Column(String)
    setor_id = Column(String)
    tamanho = Column(Integer)
    motivo = Column(String)
    alternatives_evaluated = Column(Integer)

    run = relationship("AllocationRun", back_populates="exceptions")


class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("allocation_runs.id"))
    team_id = Column(String)
    acao = Column(String)  # rejeitar | alterar
    sala_id = Column(String, nullable=True)  # nova sala, se acao == alterar
    usuario = Column(String, default="coordenador-geral")
    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("AllocationRun", back_populates="interventions")
