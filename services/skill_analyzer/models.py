from db import Base, str_uniq, int_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class Skill(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    course: Mapped[str]

class Synonym(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)