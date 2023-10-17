from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta, datetime
import pymongo
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated, Optional
from models.request_models import CreateUserRequest
from models.response_models import TokenResponse
from jose import jwt, JWTError
from models.db_models import User
import os
from dotenv import load_dotenv
load_dotenv()
import logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("logs/auth.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

SECRET_KEY=os.environ["SECRET_KEY"]
ALGORITHM=os.environ["ALGORITHM"]

def get_mongo_client():
    uri = os.environ["MONGODB_URL"]
    return pymongo.MongoClient(uri)

client = get_mongo_client()
USER_COLLECTION = client[os.environ["DATABASE"]]["user"]

try:
    client.admin.command('ping')
    logger.info("Auth connected to MongoDB!")
except Exception as e:
    logger.exception(e)

@router.post("/sign-up", status_code=status.HTTP_201_CREATED) 
async def sign_up_user(createUserRequest: CreateUserRequest):
    user = USER_COLLECTION.find_one({'email': createUserRequest.email})
    if user:
        raise HTTPException(status_code=401, detail="user already exists")
    user = User(
        name=createUserRequest.name,
        email=createUserRequest.email,
        hashed_password=bcrypt_context.hash(createUserRequest.password),
        role="user"
    )
    if user.name=="" or user.email=="":
        raise HTTPException(detail="name or email can not empty", status_code=status.HTTP_400_BAD_REQUEST)
    USER_COLLECTION.insert_one(user.__dict__)


def authenticate_user(username: str, password: str):
    user = USER_COLLECTION.find_one({"email": username})
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user['hashed_password']):
        return False
    
    return user

def create_access_token(username: str, user_id: str, role: str, expires_in: timedelta):
    encode = {
        "email": username,
        "id": user_id,
        "exp": datetime.utcnow() + expires_in,
        "role": role
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        email: str = payload.get('email')
        id: str = payload.get('id')
        role: str = payload.get('role')
        
        if email is None or id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="unable to validate user")

        return {'email': email, 'id': id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="unable to validate user")
    

@router.post("/login", response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="unable to validate user")
    token = create_access_token(user['email'], str(user['_id']), user['role'], timedelta(hours=2))
    return {"name": user["name"], "access_token": token, "token_type": "bearer"}