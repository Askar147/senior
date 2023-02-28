from sqlalchemy.orm import Session

from . import models, schemes


def get_result(db: Session, key: int):
    return db.query(models.Result).filter(models.Result.key == key).all()
