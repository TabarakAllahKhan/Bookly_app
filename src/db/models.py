#This imports necessary components from the SQLModel 
# library, which is used to define SQL database models in Python.

from sqlmodel import Relationship, SQLModel,Field,Column
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


from sqlmodel import SQLModel,Field,Column
import uuid
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg

class User(SQLModel,table=True):
    '''This class is used to define the User model for authentication purposes.'''
    __tablename__="users"
    
    uid:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    role:str=Field(sa_column=Column(pg.VARCHAR,nullable=False,server_default="user"))
    username:str = Field(index=True, nullable=False, unique=True)
    email:str = Field(index=True, nullable=False, unique=True)
    password_hash:str=Field(nullable=False,exclude=True)
    is_verified:bool = Field(default=False, nullable=False)
    created_at:datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at:datetime = Field(default_factory=datetime.now, nullable=False)    


def __repr__(self) -> str:
    return f"<User{self.username}>"


class Review(SQLModel,table=True):
    __tablename__="reviews"
    
    uid:uuid.UUID=Field(sa_column=Column(pg.UUID,nullable=False,primary_key=True,default=uuid.uuid4))
    rating:int=Field(lt=5)
    review_txt:str
    user_uid:Optional[uuid.UUID]=Field(default=None,foreign_key="users.uid")
    book_uid:Optional[uuid.UUID]=Field(default=None,foreign_key="books.id")
    created_at:datetime=Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    updated_at:datetime=Field(sa_column=Column(pg.TIMESTAMP,default=datetime.now))
    user:Optional[User]=Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"