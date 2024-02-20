from sqlalchemy import Integer, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .db import engine


class Base(DeclarativeBase):
    pass


class Bap(Base):
    __tablename__ = "baps"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)


Base.metadata.create_all(engine)
