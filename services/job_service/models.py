from job_service.db import Base, str_null_true, int_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class Vacancy(Base):
    __tablename__ = "vacancies"
    id: Mapped[int_pk]
    name: Mapped[str]
    description: Mapped[str]
    employer: Mapped[str]
    salary: Mapped[str_null_true]
    employment: Mapped[str_null_true]
    schedule: Mapped[str_null_true]
    expirience: Mapped[str_null_true]
    area: Mapped[str_null_true]