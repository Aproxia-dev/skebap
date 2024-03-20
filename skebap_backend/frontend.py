from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from jinja2_fragments.fastapi import Jinja2Blocks
from pathlib import Path
from .api import read_bap, BapModel

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


@router.get("/bap/{bap_id}", response_class=HTMLResponse)
async def view(request: Request, bap_id: int):
    block = None

    if "hx-target" in request.headers:
        block = request.headers["hx-target"]

    bap = await read_bap(bap_id)
    if not isinstance(bap, BapModel):
        raise HTTPException(500, "Invalid Bap data")

    return templates.TemplateResponse(
        "view.html",
        {"request": request, "monaco": True, "bap_content": bap.content},
        block_name=block,
    )
