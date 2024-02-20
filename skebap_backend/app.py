from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from skebap_backend import api, frontend

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static"))
)

app.include_router(api.router, prefix="/api")
app.include_router(frontend.router, include_in_schema=False)
