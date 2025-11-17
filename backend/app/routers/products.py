from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List
from pydantic import BaseModel
from ..db import get_db
from .auth import get_admin
from bson import ObjectId
import os
import time

router  = APIRouter()

class  ProductOut(BaseModel):
    id: str
    name: str
    description: str
    image: str

def serialize_product(product):
  return{"id": str(product["_id"]), "name" : product["name"],"description" : product["description"], "image":product["image"]}

@router.get("/", response_model=List[ProductOut])
async def list_products(db=Depends(get_db)):
    products = db["products"].find({})
    items = []
    async for p in products:
      items.append(serialize_product(p))
    return items

