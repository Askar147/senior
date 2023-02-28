from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=False, index=True)
    order_number = Column(Integer, index=True)
    result = Column(String, index=True)
