#This imports necessary components from the SQLModel 
# library, which is used to define SQL database models in Python.

from sqlmodel import SQLModel,Field,Column
#this import brings in PostgreSQL-specific 
# features from SQLAlchemy (which SQLModel is built on top of).
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from typing import Optional
import uuid
class Book(SQLModel,table=True):
    __tablename__="books"
    '''
    This class is used to create a database table for books.
    In the PostgreSQL database, it will create a table named 'book' with the following columns:
    id, title, author, year, isbn, pages, price, available, summary
    '''
    id: uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True,index=True,nullable=False)
    title: str
    author: str
    year: int
    isbn: str
    pages: int
    price: float
    available: bool
    summary: str
    user_uid:Optional[uuid.UUID]=Field(default=None,foreign_key="users.uid")
    created_at: datetime=Field(default_factory=datetime.now)
    updated_at: datetime=Field(default_factory=datetime.now)

    def __repr__(self):
        return f"Book {self.title}"