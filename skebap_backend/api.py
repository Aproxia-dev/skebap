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
	lang: Optional[str]


class BapResponse(BapModel):
	id: Optional[int] = None
	content: str
	lang: Optional[str]
	creation_time: datetime
	valid_until: datetime

class UserModel(BaseModel):
	email: str

class NewUserRequest(UserModel):
	password: str

class UserResponse(UserModel):
	id: int

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
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

def create_access_token(data: dict, expires_delta: timedelta = timedelta(days = ACCESS_TOKEN_EXPIRE_DAYS)):
	to_encode = data.copy()
	expire = datetime.now() + expires_delta
	to_encode.update({"exp": expire})
	ret = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return ret

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
	cred_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		uid = payload.get("uid")
		if uid == None:
			raise cred_exception
		token_data = TokenData(uid = uid)
	except JWTError:
		raise cred_exception
	user = Session(engine).execute(select(User).where(User.id == uid)).first()[0]
	if user == None:
		raise cred_exception
	return UserResponse(id = user.id, email = user.email)


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
	user = Session(engine).execute(select(User).where(User.email == form_data.username)).first()[0]
	if user == None:
		raise HTTPException(status_code=401, detail="Incorrect username or password")
	if auth_user(user, form_data.password) == False:
		raise HTTPException(status_code=401, detail="Incorrect username or password")
	access_token = create_access_token(data={"uid": user.id})
	return Token(access_token=access_token, token_type="bearer")

@router.post("/register")
async def register(user: NewUserRequest) -> Token:
	if Session(engine).execute(select(User).where(User.email == user.email)).first() != None:
		raise HTTPException(status_code=403, detail="A user with that email already exists")
	new_user = User(
		email = user.email,
		pass_hash = get_password_hash(user.password)
	)

	with Session(engine) as session:
		session.add(new_user)
		session.commit()
		session.refresh(new_user)

	access_token = create_access_token(data={"uid": new_user.id})
	return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me")
async def read_users_me(current_user: Annotated[UserResponse, Depends(get_current_user)]) -> UserResponse:
	return current_user


@router.get("/{bap_id}")
async def read_bap(bap_id: int) -> BapResponse:
	result = Session(engine).execute(select(Bap).where(Bap.id == bap_id)).first()
	if result == None:
		raise HTTPException(status_code=404, detail="Bap not found")
	result = result[0]
	return BapResponse(
		id=result.id,
		content=result.text,
		lang=result.lang,
		creation_time=result.creation_time,
		valid_until=result.valid_until
	)


@router.post("/")
async def new_bap(bap: BapRequest) -> BapResponse:
	creation_time = datetime.now()
	if bap.lang != None and Session(engine).execute(select(Lang).where(Lang.lang == bap.lang)).first() == None:
		raise HTTPException(status_code=400, detail="Invalid language")
	new_bap = Bap(
		text=bap.content,
		lang=bap.lang,
		creation_time=creation_time,
		valid_until=creation_time + timedelta(days=14)
	)

	with Session(engine) as session:
		session.add(new_bap)
		session.commit()
		session.refresh(new_bap)

	return BapResponse(
		id=new_bap.id,
		content=new_bap.text,
		lang=new_bap.lang,
		creation_time=new_bap.creation_time,
		valid_until=new_bap.valid_until
	)