from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.base.db import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    questions = relationship("Question", back_populates="subject")