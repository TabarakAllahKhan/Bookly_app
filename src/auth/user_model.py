from sqlmodel import SQLModel,Field
import uuid
from datetime import datetime

class User(SQLModel,table=True):
    '''This class is used to define the User model for authentication purposes.'''
    __tablename__="users"
    
    uid:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    username:str = Field(index=True, nullable=False, unique=True)
    email:str = Field(index=True, nullable=False, unique=True)
    password_hash:str=Field(nullable=False,exclude=True)
    is_verified:bool = Field(default=False, nullable=False)
    created_at:datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at:datetime = Field(default_factory=datetime.now, nullable=False)    


def __repr__(self) -> str:
    return f"<User{self.username}>"


