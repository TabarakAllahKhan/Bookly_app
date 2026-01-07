from pydantic import BaseModel,Field,EmailStr
import uuid
from datetime import datetime
from typing import ClassVar
class UserCreateModel(BaseModel):
    '''
    This model is used for validating user creation data.
    When the user sends a signup request, the data is validated against this model.
    Attributes:
    username (str): The username of the user.
    email (str): The email of the user.
    password (str): The password of the user.
    
    '''
    username:str=Field(max_length=8)
    email:str = Field(max_length=40)
    password:str = Field(min_length=6, max_length=20)

class UserModel(BaseModel):
    uid:uuid.UUID
    username:str
    email:str
    is_verified:bool
    created_at:datetime
    updated_at:datetime

class UserLoginModel(BaseModel):
    email:EmailStr=Field(max_length=40)
    password:str=Field(min_length=6)
    

class Config:
    orm_mode = True