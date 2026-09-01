from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    andar: int
    capacidade: int
    tipo: str
    recursos: List[str] = []
    acessivel: bool
    disponivel: bool


class RoomUpdate(BaseModel):
    disponivel: Optional[bool] = None
    capacidade: Optional[int] = None


class SectorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    coordenador: str


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    setor_id: str
    tamanho: int
    prioridade: str
    grupo_proximidade: Optional[str] = None
    req_equip: Optional[List[str]] = None


class TeamUpdate(BaseModel):
    tamanho: Optional[int] = None
    prioridade: Optional[str] = None


class ConstraintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    ativa: bool
    tipo: str
    alvo: Optional[str] = None
    valor: Optional[object] = None
    descricao: str


class ConstraintUpdate(BaseModel):
    ativa: Optional[bool] = None


class AllocationResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: str
    team_name: str
    setor_id: str
    tamanho: int
    sala_id: str
    andar: int
    capacidade: int
    ocupacao: float
    alternatives_evaluated: int
    status: str


class AllocationExceptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: str
    team_name: str
    setor_id: str
    tamanho: int
    motivo: str
    alternatives_evaluated: int


class AllocationRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime
    usuario: str
    algoritmo: str
    equipes_analisadas: int
    salas_analisadas: int
    equipes_alocadas: int
    equipes_nao_alocadas: int
    violacoes: int
    ocupacao_prevista: float
    tempo_ms: float


class AllocationRunDetail(AllocationRunOut):
    results: List[AllocationResultOut] = []
    exceptions: List[AllocationExceptionOut] = []


class InterventionIn(BaseModel):
    team_id: str
    acao: str  # "rejeitar" | "alterar"
    sala_id: Optional[str] = None


class TrustTestOut(BaseModel):
    titulo: str
    descricao: str
    passou: bool
    detalhe: str


class MonitoringOut(BaseModel):
    execucoes: int
    tempo_medio_ms: float
    taxa_alocacao_media: float
    ocupacao_media: float
    intervencoes: int
    erros: int
