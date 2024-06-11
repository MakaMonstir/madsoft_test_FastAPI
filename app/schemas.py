from pydantic import BaseModel

class MemeBase(BaseModel):
    title: str
    description: str
    image_url: str

class Meme(MemeBase):
    id: int

    class Config:
        orm_mode = True
