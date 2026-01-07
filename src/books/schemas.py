from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
class Book(BaseModel):
    '''This class represents a book with various attributes.
       It is used for data validation in FastAPI endpoints.
    '''
    id: uuid.UUID
    title: str
    author: str
    year: int
    isbn: str
    pages: int
    price: float
    available: bool
    summary: str
    created_at: datetime
    updated_at: datetime

class BookUpdate(BaseModel):
    '''This class represents the fields that can be updated for a book.
       All fields are optional to allow partial updates.
    '''
    id:Optional[uuid.UUID]=None
    title:Optional[str]=None
    author:Optional[str]=None
    price:Optional[float]=None

class BookCreateModel(BaseModel):
    '''This class represents the data required to create a new book.
       All fields are mandatory except for uid, created_at, and updated_at which are auto-generated.
    '''
    title: str
    author: str
    year: int
    isbn: str
    pages: int
    price: float
    available: bool
    summary: str

class Config:
      orm_mode = True