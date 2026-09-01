from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, SessionLocal, engine, get_db
from .engine import generate_allocation, naive_allocation
from .seed import seed_if_empty
from .trust_tests import run_trust_tests

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema Inteligente de Gestão de Espaços Corporativos",
    description="API do motor de alocação — allocation-engine-v1",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # protótipo — em produção, restringir ao domínio do front-end
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _room_dict(r: models.Room) -> dict:
    return {"id": r.id, "andar": r.andar, "capacidade": r.capacidade, "tipo": r.tipo,
            "recursos": r.recursos or [], "acessivel": r.acessivel, "disponivel": r.disponivel}


def _team_dict(t: models.Team) -> dict:
    return {"id": t.id, "nome": t.nome, "setor_id": t.setor_id, "tamanho": t.tamanho,
            "prioridade": t.prioridade, "grupo_proximidade": t.grupo_proximidade, "req_equip": t.req_equip}


def _constraint_dict(c: models.Constraint) -> dict:
    return {"id": c.id, "ativa": c.ativa, "tipo": c.tipo, "alvo": c.alvo, "valor": c.valor, "descricao": c.descricao}


def _current_state(db: Session):
    rooms = [_room_dict(r) for r in db.query(models.Room).all()]
    teams = [_team_dict(t) for t in db.query(models.Team).all()]
    constraints = [_constraint_dict(c) for c in db.query(models.Constraint).all()]
    return rooms, teams, constraints


# ---------------------------------------------------------------------------
# salas
# ---------------------------------------------------------------------------

@app.get("/api/rooms", response_model=List[schemas.RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).order_by(models.Room.andar, models.Room.id).all()


@app.patch("/api/rooms/{room_id}", response_model=schemas.RoomOut)
def update_room(room_id: str, payload: schemas.RoomUpdate, db: Session = Depends(get_db)):
    room = db.get(models.Room, room_id)
    if not room:
        raise HTTPException(404, "Sala não encontrada")
    if payload.disponivel is not None:
        room.disponivel = payload.disponivel
    if payload.capacidade is not None:
        room.capacidade = payload.capacidade
    db.commit()
    db.refresh(room)
    return room


# ---------------------------------------------------------------------------
# setores
# ---------------------------------------------------------------------------

@app.get("/api/sectors", response_model=List[schemas.SectorOut])
def list_sectors(db: Session = Depends(get_db)):
    return db.query(models.Sector).all()


# ---------------------------------------------------------------------------
# equipes
# ---------------------------------------------------------------------------

@app.get("/api/teams", response_model=List[schemas.TeamOut])
def list_teams(db: Session = Depends(get_db)):
    return db.query(models.Team).all()


@app.patch("/api/teams/{team_id}", response_model=schemas.TeamOut)
def update_team(team_id: str, payload: schemas.TeamUpdate, db: Session = Depends(get_db)):
    team = db.get(models.Team, team_id)
    if not team:
        raise HTTPException(404, "Equipe não encontrada")
    if payload.tamanho is not None:
        team.tamanho = payload.tamanho
    if payload.prioridade is not None:
        team.prioridade = payload.prioridade
    db.commit()
    db.refresh(team)
    return team


# ---------------------------------------------------------------------------
# restrições
# ---------------------------------------------------------------------------

@app.get("/api/constraints", response_model=List[schemas.ConstraintOut])
def list_constraints(db: Session = Depends(get_db)):
    return db.query(models.Constraint).all()


@app.patch("/api/constraints/{constraint_id}", response_model=schemas.ConstraintOut)
def update_constraint(constraint_id: str, payload: schemas.ConstraintUpdate, db: Session = Depends(get_db)):
    c = db.get(models.Constraint, constraint_id)
    if not c:
        raise HTTPException(404, "Restrição não encontrada")
    if payload.ativa is not None:
        c.ativa = payload.ativa
    db.commit()
    db.refresh(c)
    return c


# ---------------------------------------------------------------------------
# motor de alocação + governança
# ---------------------------------------------------------------------------

@app.post("/api/allocate", response_model=schemas.AllocationRunDetail)
def allocate(db: Session = Depends(get_db)):
    rooms, teams, constraints = _current_state(db)
    run = generate_allocation(rooms, teams, constraints)

    total_cap = sum(r["capacidade"] for r in rooms if r["disponivel"])
    total_ocupado = sum(r["tamanho"] for r in run["results"])
    ocupacao_pct = (total_ocupado / total_cap * 100) if total_cap else 0.0

    db_run = models.AllocationRun(
        timestamp=datetime.utcnow(),
        usuario="coordenador-geral",
        algoritmo="allocation-engine-v1",
        equipes_analisadas=len(teams),
        salas_analisadas=len(rooms),
        equipes_alocadas=len(run["results"]),
        equipes_nao_alocadas=len(run["exceptions"]),
        violacoes=run["violations"],
        ocupacao_prevista=ocupacao_pct,
        tempo_ms=run["tempo_ms"],
    )
    db.add(db_run)
    db.flush()  # obtém db_run.id

    for r in run["results"]:
        db.add(models.AllocationResult(run_id=db_run.id, **r_without_score(r)))
    for e in run["exceptions"]:
        db.add(models.AllocationException(run_id=db_run.id, **e))

    db.commit()
    db.refresh(db_run)
    return db_run


def r_without_score(r: dict) -> dict:
    return {
        "team_id": r["team_id"], "team_name": r["team_name"], "setor_id": r["setor_id"],
        "tamanho": r["tamanho"], "sala_id": r["sala_id"], "andar": r["andar"],
        "capacidade": r["capacidade"], "ocupacao": r["ocupacao"],
        "alternatives_evaluated": r["alternatives_evaluated"],
    }


@app.get("/api/allocate/baseline")
def allocate_baseline(db: Session = Depends(get_db)):
    rooms, teams, _ = _current_state(db)
    return naive_allocation(rooms, teams)


@app.get("/api/governance", response_model=List[schemas.AllocationRunOut])
def list_governance(db: Session = Depends(get_db)):
    return db.query(models.AllocationRun).order_by(models.AllocationRun.id.desc()).all()


@app.get("/api/governance/{run_id}", response_model=schemas.AllocationRunDetail)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(models.AllocationRun, run_id)
    if not run:
        raise HTTPException(404, "Execução não encontrada")
    return run


@app.post("/api/governance/{run_id}/intervene", response_model=schemas.AllocationRunDetail)
def intervene(run_id: int, payload: schemas.InterventionIn, db: Session = Depends(get_db)):
    run = db.get(models.AllocationRun, run_id)
    if not run:
        raise HTTPException(404, "Execução não encontrada")
    result = next((r for r in run.results if r.team_id == payload.team_id), None)
    if not result:
        raise HTTPException(404, "Recomendação não encontrada nesta execução")

    if payload.acao == "rejeitar":
        result.status = "rejeitada"
    elif payload.acao == "alterar":
        if not payload.sala_id:
            raise HTTPException(400, "sala_id é obrigatório para a ação 'alterar'")
        nova_sala = db.get(models.Room, payload.sala_id)
        if not nova_sala:
            raise HTTPException(404, "Sala informada não existe")
        if nova_sala.capacidade < result.tamanho:
            raise HTTPException(400, "A nova sala não comporta o tamanho da equipe")
        result.sala_id = nova_sala.id
        result.andar = nova_sala.andar
        result.capacidade = nova_sala.capacidade
        result.ocupacao = result.tamanho / nova_sala.capacidade
        result.status = "alterada"
    else:
        raise HTTPException(400, "acao deve ser 'rejeitar' ou 'alterar'")

    db.add(models.Intervention(run_id=run_id, team_id=payload.team_id, acao=payload.acao, sala_id=payload.sala_id))
    db.commit()
    db.refresh(run)
    return run


# ---------------------------------------------------------------------------
# painel de confiança (testes metamórficos ao vivo)
# ---------------------------------------------------------------------------

@app.get("/api/trust-tests", response_model=List[schemas.TrustTestOut])
def trust_tests(db: Session = Depends(get_db)):
    rooms, teams, constraints = _current_state(db)
    return run_trust_tests(rooms, teams, constraints)


# ---------------------------------------------------------------------------
# observabilidade
# ---------------------------------------------------------------------------

@app.get("/api/monitoring", response_model=schemas.MonitoringOut)
def monitoring(db: Session = Depends(get_db)):
    runs = db.query(models.AllocationRun).all()
    interventions = db.query(models.Intervention).count()
    if not runs:
        return schemas.MonitoringOut(execucoes=0, tempo_medio_ms=0, taxa_alocacao_media=0, ocupacao_media=0, intervencoes=interventions, erros=0)
    tempo_medio = sum(r.tempo_ms for r in runs) / len(runs)
    taxa_media = sum(
        r.equipes_alocadas / (r.equipes_alocadas + r.equipes_nao_alocadas) if (r.equipes_alocadas + r.equipes_nao_alocadas) else 0
        for r in runs
    ) / len(runs) * 100
    ocupacao_media = sum(r.ocupacao_prevista for r in runs) / len(runs)
    return schemas.MonitoringOut(
        execucoes=len(runs), tempo_medio_ms=tempo_medio, taxa_alocacao_media=taxa_media,
        ocupacao_media=ocupacao_media, intervencoes=interventions, erros=0,
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
