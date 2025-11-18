from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from ..db import get_db
from .auth import get_admin
from bson import ObjectId
from datetime import datetime, timezone
import os


router = APIRouter()

class ProductIn(BaseModel):
  name:str
  description : Optional[str] = None
  image_url : Optional[HttpUrl] = None
  date : Optional[datetime] = None
class  ProductOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    date: Optional[datetime] = None
    created_at: datetime

def to_out(doc) -> ProductOut:
  return ProductOut(
    id=str(doc["_id"]),
    name=doc["name"],
    description = doc.get("description"),
    image_url = doc.get("image_url"),
    image_path = doc.get("image_path"),
    date = doc.get("date"),
    created_at = doc["created_at"],
  )



@router.get("/", response_model=List[ProductOut])
async def list_products(admin=Depends(get_admin), db=Depends(get_db)):
    cursor = db["products"].find().sort("created_at", -1)
    items: List[ProductOut] = []
    async for doc in cursor:
      items.append(to_out(doc))
    return items
  
@router.post("/", response_model=ProductOut)
async def create_product(data: ProductIn, admin=Depends(get_admin), db=Depends(get_db)):
  prod = {
    "name": data.name,
    "description": data.description,
    "image_url": str(data.image_url) if data.image_url else None,
    "date": data.date,
    "created_at": datetime.now(timezone.utc),
  }
  res = await db["products"].insert_one(prod)
  doc = await db["products"].find_one({"_id":res.inserted_id})
  return to_out(doc)


@router.get("/{id}", response_model=ProductOut)
async def get_product(id:str, admin=Depends(get_admin), db = Depends(get_db)):
  try:
    oid = ObjectId(id)
  except Exception:
    raise HTTPException(status_code=400,detail="Id invalido")
  doc = await db["products"].find_one({"_id":oid})
  if not doc:
    raise HTTPException(status_code=404 , detail="No se encontro el producto")
  return to_out(doc)


@router.put("/{id}", response_model=ProductOut)
async def update_product(id:str, data: ProductIn, admin= Depends(get_admin), db= Depends(get_db)):
  try:
    oid = ObjectId(id)
  except Exception:
    raise HTTPException(status_code=400, detail="Id invalido")
  update = {
    "name": data.name,
    "description" : data.description,
    "image_url": str(data.image_url) if data.image_url else None,
    "date":data.date
  }
  await db["products"].update_one({"_id" : oid}, {"$set":update})
  doc = await db["products"].find_one({"_id":oid})
  if not doc:
    raise HTTPException(status_code=404, detail="No se encontro el producto")
  return to_out(doc)

@router.delete("/{id}")
async def delete_product(id:str, admin = Depends(get_admin), db=Depends(get_db)):
  try:
    oid = ObjectId(id)
  except Exception:
    raise HTTPException(status_code=400, detail="Id invalido")
  res = await db["products"].delete_one({"_id":oid})
  if res.deleted_count == 0 :
    raise HTTPException(status_code=404, detail="Not found")
  return {"ok" :True}


@router.post("/{id}/image", response_model=ProductOut)
async def upload_image(id: str, file: UploadFile = File(...), admin=Depends(get_admin), db=Depends(get_db)):
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")
    os.makedirs("backend/uploads", exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    path = f"backend/uploads/{id}{ext}"
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    await db["products"].update_one({"_id": oid}, {"$set": {"image_path": path}})
    doc = await db["products"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return to_out(doc)