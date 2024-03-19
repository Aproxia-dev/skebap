from datetime import datetime, timedelta
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from .models import Bap
from .db import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional


class BapModel(BaseModel):
    content: str


class BapRequest(BapModel):
    content: str


class BapResponse(BapModel):
    id: Optional[int] = None
    content: str
    creation_time: datetime
    valid_until: datetime

class UserModel(BaseModel):
    email: str
    passHash: str

router = APIRouter()


@router.get("/{bap_id}")
async def read_bap(bap_id: int) -> BapResponse:
    result = Session(engine).execute(select(Bap).where(Bap.id == bap_id)).first()
    if result == None:
        raise HTTPException(status_code=404, detail="Bap not found")
    return BapResponse(
		id=result[0].id,
		content=result[0].text,
        creation_time=result[0].creation_time,
        valid_until=result[0].valid_until
	)


@router.post("/")
async def new_bap(bap: BapRequest) -> BapResponse:
    new_bap = Bap(
        text=bap.content,
        creation_time=datetime.now(),
        valid_until=datetime.now() + timedelta(days=14)
    )

    with Session(engine) as session:
        session.add(new_bap)
        session.commit()
        session.refresh(new_bap)

    return BapResponse(
        id=new_bap.id,
        content=new_bap.text,
        creation_time=new_bap.creation_time,
        valid_until=new_bap.valid_until
    )