from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DateTime, Integer, Text
from .db import engine


class Base(DeclarativeBase):
    pass


class Bap(Base):
	__tablename__ = "baps"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	text: Mapped[str] = mapped_column(Text, nullable=False)
	author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
	lang: Mapped[str] = mapped_column(ForeignKey("langs.lang"), nullable=True)
	creation_time: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
	valid_until: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    pass_hash: Mapped[str] = mapped_column(Text, nullable=False)


class Lang(Base):
    __tablename__ = "langs"

    lang: Mapped[str] = mapped_column(Text, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    file_extension: Mapped[str] = mapped_column(Text, nullable=False)


Base.metadata.create_all(engine)

base_langs = [
	Lang(lang="javascript", display_name="JavaScript", file_extension=".js"),
	Lang(lang="python",     display_name="Python",     file_extension=".py"),
	Lang(lang="java",       display_name="Java",       file_extension=".java"),
	Lang(lang="cpp",        display_name="C++",        file_extension=".cpp"),
	Lang(lang="csharp",     display_name="C#",         file_extension=".cs"),
	Lang(lang="php",        display_name="PHP",        file_extension=".php"),
	Lang(lang="typescript", display_name="TypeScript", file_extension=".ts"),
	Lang(lang="go",         display_name="Go",         file_extension=".go"),
	Lang(lang="lua",        display_name="Lua",        file_extension=".lua"),
	Lang(lang="shell",      display_name="Shell",      file_extension=".sh"),
	Lang(lang="rust",       display_name="Rust",       file_extension=".rs"),
	Lang(lang="kotlin",     display_name="Kotlin",     file_extension=".kt"),
]

with Session(engine) as session:
    if session.execute(select(Lang)).first() is None:
        session.add_all(base_langs)
        session.commit()
