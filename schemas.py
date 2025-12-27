from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    price: int

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    price: int | None = None

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    price: int

    class Config:
        from_attributes = True
