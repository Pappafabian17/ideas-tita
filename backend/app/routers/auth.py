from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from ..db import get_db
from ..security import verify_password, get_password_hash, create_access_token, decode_token


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    
class Token(BaseModel):
    access_token: str
    token_type : str = "bearer"
    
async def get_admin(db=Depends(get_db),token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        user = await db["users"].find_one({"username": username, "role" : "admin"})
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
        
@router.post("/signup", response_model=Token)
async def signup(data: UserCreate, db=Depends(get_db)):
    existing =  await db["users"].find_one({"role":"admin"})
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    await db["users"].insert_one({"username":data.username, "password":get_password_hash(data.password),"role":"admin"})
    token = create_access_token(data.username)
    return {"access_token": token, "token_type":"bearer"}

@router.post("/login",response_model=Token)
async def login(form_data:OAuth2PasswordRequestForm = Depends(),db=Depends(get_db)):
    user = await db["users"].find_one({"username":form_data.username, "role":"admin"})
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(user["username"])
    return {"access_token":token, "token_type":"bearer"}