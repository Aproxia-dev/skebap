from datetime import datetime
from sqlalchemy.types import DateTime, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from .db import engine


class Base(DeclarativeBase):
    pass


class Bap(Base):
    __tablename__ = "baps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    creation_time: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    valid_until: Mapped[int] = mapped_column(DateTime(), nullable=True)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    pass_hash: Mapped[str] = mapped_column(Text, nullable=False)

Base.metadata.create_all(engine)
