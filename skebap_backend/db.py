import os
from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

engine = create_engine(
    URL.create(
        "postgresql",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host="db",
        database="appdb",
    )
)

if not database_exists(engine.url):
    create_database(engine.url)
