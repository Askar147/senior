from sqlalchemy.orm import Session

from . import models, schemes


def get_result(db: Session, user_id: int):
    return db.query(models)
