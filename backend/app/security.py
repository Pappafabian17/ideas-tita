import os
import time
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt

load_dotenv()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET","NO HAY SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.environ.get("JWT_EXPIRE_SECONDS","3600"))


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(plain):
    return pwd_context.hash(plain)

def create_access_token(sub:str):
    payload = {"sub":sub, "exp":int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS}
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

def decode_token(token:str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    