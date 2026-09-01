from sqlalchemy.orm import Session

from . import models
from .seed_data import ROOMS, SECTORS, TEAMS, CONSTRAINTS


def seed_if_empty(db: Session) -> None:
    if db.query(models.Room).first():
        return  # já populado

    for r in ROOMS:
        db.add(models.Room(**r, disponivel=True))
    for s in SECTORS:
        db.add(models.Sector(**s))
    for t in TEAMS:
        db.add(models.Team(**t))
    for c in CONSTRAINTS:
        db.add(models.Constraint(**c, ativa=True))
    db.commit()
