from sqlalchemy.orm import Session

from . import models, schemes


def get_result(db: Session, key: str):
    return db.query(models.Result).filter(models.Result.key == key).all()


def create_result(db: Session, key: str, order: int, result: str):
    db_result = models.Result(key=key, order_number=order, result=result)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result
