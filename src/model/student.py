from sqlalchemy import Column, Integer, String

from src.base.db import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    group = Column(String)
    faculty = Column(String)