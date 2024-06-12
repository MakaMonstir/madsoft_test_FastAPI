from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import httpx
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(
    prefix="/memes",
    tags=["memes"],
)

@router.get("/", response_model=List[schemas.Meme])
def list_memes(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    memes = crud.get_memes(db, skip=skip, limit=limit)
    return memes

@router.get("/{meme_id}", response_model=schemas.Meme)
def read_meme(meme_id: int, db: Session = Depends(database.get_db)):
    db_meme = crud.get_meme(db, meme_id=meme_id)
    if db_meme is None:
        raise HTTPException(status_code=404, detail="Meme not found")
    return db_meme

@router.post("/", response_model=schemas.Meme)
async def create_meme(title: str = Form(...),  description: str = Form(...), image_file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    async with httpx.AsyncClient() as client:
        files = {'file':(image_file.filename, image_file.file, image_file.content_type)}
        response = await client.post("http://media:8001/upload", files=files)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to upload image")
        
        image_url = response.json().get("filename")
    
    meme = schemas.MemeUpdate(title=title, description=description, image_url=image_url)
    return crud.create_meme(db=db, meme=meme)

@router.put("/{meme_id}", response_model=schemas.Meme)
async def update_meme(meme_id: int, title: str = Form(...), description: str = Form(...), image_file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    async with httpx.AsyncClient() as client:
        files = {'file':(image_file.filename, image_file.file, image_file.content_type)}
        response = await client.post("http://media:8001/upload", files=files)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to upload image")
        
        image_url = response.json().get("filename")
    
    meme = schemas.MemeUpdate(title=title, description=description, image_url=image_url)
    return crud.update_meme(db=db, meme_id=meme_id, meme = meme)

@router.delete("/{meme_id}", response_model=schemas.Meme)
def delete_meme(meme_id: int, db: Session = Depends(database.get_db)):
    return crud.delete_meme(db=db, meme_id=meme_id)
