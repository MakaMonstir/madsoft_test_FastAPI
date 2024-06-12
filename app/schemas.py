from typing import Optional
from pydantic import BaseModel
from fastapi import UploadFile, File

class MemeBase(BaseModel):
    title: str
    description: str

class MemeCreate(MemeBase):
    pass

class MemeUpdate(MemeBase):
    image_url: Optional[str] = None

class Meme(MemeUpdate):
    id: int

    class Config:
        orm_mode = True
