from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from .models import Bap, User, Lang
from .db import engine
from sqlalchemy import select
from sqlalchemy.engine import Result, Row
from sqlalchemy.orm import Session
from typing import Annotated, Optional

SECRET_KEY = "b9affae87e0d93e7f46d21dd8cb663460459516c529a79aff2be11ef256a93c4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    uid: int


class BapModel(BaseModel):
    content: str


class BapRequest(BapModel):
    content: str
    lang: str


class BapResponse(BapModel):
    id: Optional[int] = None
    content: str
    author: Optional[int]
    lang: Optional[str]
    creation_time: datetime
    valid_until: datetime


class BapsResponse(BaseModel):
    baps: list[BapResponse]


class UserModel(BaseModel):
    email: str


class NewUserRequest(UserModel):
    password: str


class UserResponse(UserModel):
    id: int


class LangResponse(BaseModel):
    lang: str
    display_name: str
    file_extension: str


class LangsResponse(BaseModel):
    langs: list[LangResponse]


router = APIRouter()
required_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password + SECRET_KEY)


def verify_password(password: str, pass_hash: str):
    return pwd_context.verify(password + SECRET_KEY, pass_hash)


def auth_user(user: Row, password: str):
    if not user:
        return False
    if not verify_password(password, user.pass_hash):
        return False
    return user


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    ret = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return ret


async def get_current_user(token: str):
    if token == None:
        return None
    cred_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("uid")
        if uid == None:
            raise cred_exception
        token_data = TokenData(uid=uid)
    except JWTError:
        raise cred_exception
    user = Session(engine).execute(select(User).where(User.id == uid)).first()
    if user == None:
        raise cred_exception
    else:
        user = user[0]
    return UserResponse(id=user.id, email=user.email)


async def get_optional_user(token: Annotated[str, Depends(optional_oauth2_scheme)]):
    if token == None:
        return None
    else:
        return await get_current_user(token)


async def get_required_user(token: Annotated[str, Depends(required_oauth2_scheme)]):
    return await get_current_user(token)


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = (
        Session(engine)
        .execute(select(User).where(User.email == form_data.username))
        .first()
    )
    if user == None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    else:
        user = user[0]
    if auth_user(user, form_data.password) == False:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"uid": user.id})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register(user: NewUserRequest) -> Token:
    if (
        Session(engine).execute(select(User).where(User.email == user.email)).first()
        != None
    ):
        raise HTTPException(
            status_code=403, detail="A user with that email already exists"
        )
    new_user = User(email=user.email, pass_hash=get_password_hash(user.password))

    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    access_token = create_access_token(data={"uid": new_user.id})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/self")
async def read_self(
    current_user: Annotated[UserResponse, Depends(get_required_user)]
) -> UserResponse:
    return current_user


@router.get("/lang/{lang_id}")
async def fetch_lang(lang_id: str) -> LangResponse:
    result = Session(engine).execute(select(Lang).where(Lang.lang == lang_id)).first()
    if result == None:
        raise HTTPException(status_code=404, detail="Lang not found")
    result = result[0]
    return LangResponse(
        lang=result.lang,
        display_name=result.display_name,
        file_extension=result.file_extension,
    )


@router.get("/langs")
async def fetch_langs() -> LangsResponse:
    ret = []

    for lang in Session(engine).execute(select(Lang)).all():
        ret.append(
            LangResponse(
                lang=lang[0].lang,
                display_name=lang[0].display_name,
                file_extension=lang[0].file_extension,
            )
        )
    return LangsResponse(langs=ret)


@router.get("/self/baps")
async def read_own_baps(
    current_user: Annotated[UserResponse, Depends(get_required_user)]
) -> BapsResponse:
    ret = []

    for bap in (
        Session(engine)
        .execute(select(Bap).where(Bap.author_id == current_user.id))
        .all()
    ):
        ret.append(
            BapResponse(
                id=bap[0].id,
                content=bap[0].text,
                author=bap[0].author_id,
                lang=bap[0].lang.lang,
                creation_time=bap[0].creation_time,
                valid_until=bap[0].valid_until,
            )
        )
    return BapsResponse(baps=ret)


@router.get("/{bap_id}")
async def read_bap(bap_id: int) -> BapResponse:
    result = Session(engine).execute(select(Bap).where(Bap.id == bap_id)).first()
    if result == None:
        raise HTTPException(status_code=404, detail="Bap not found")
    result = result[0]
    return BapResponse(
        id=result.id,
        content=result.text,
        author=result.author_id,
        lang=result.lang.lang,
        creation_time=result.creation_time,
        valid_until=result.valid_until,
    )


@router.post("/")
async def new_bap(
    bap: BapRequest,
    author: Annotated[Optional[UserResponse], Depends(get_optional_user)],
) -> BapResponse:
    creation_time = datetime.now()
    author_id = author.id if author != None else None
    if (
        bap.lang != None
        and Session(engine).execute(select(Lang).where(Lang.lang == bap.lang)).first()
        == None
    ):
        raise HTTPException(status_code=400, detail="Invalid language")
    new_bap = Bap(
        text=bap.content,
        lang_id=bap.lang,
        author_id=author_id,
        creation_time=creation_time,
        valid_until=creation_time + timedelta(days=14),
    )

    with Session(engine, expire_on_commit=False) as session:
        session.add(new_bap)
        session.commit()
        session.refresh(new_bap, attribute_names=["lang"])

    return BapResponse(
        id=new_bap.id,
        content=new_bap.text,
        author=new_bap.author_id,
        lang=new_bap.lang.lang,
        creation_time=new_bap.creation_time,
        valid_until=new_bap.valid_until,
    )
