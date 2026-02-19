from db import Base, str_uniq, int_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class Skill(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    course: Mapped[str]

