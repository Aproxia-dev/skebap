from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from jinja2_fragments.fastapi import Jinja2Blocks
from pathlib import Path

router = APIRouter()
templates = Jinja2Blocks(directory=str(Path(__file__).resolve().parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    block = None

    if "hx-target" in request.headers:
        block = request.headers["hx-target"]

    return templates.TemplateResponse(
        "new.html",
        {"request": request, "monaco": True},
        block_name=block,
    )
