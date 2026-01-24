
from pydantic import BaseModel
import uuid
from datetime import datetime


class TagSchema(BaseModel):
    uid:uuid.UUID
    name:str
    created_at:datetime


class TagCreateSchema(BaseModel):
    name:str
    

class TagAddSchema(BaseModel):
    tags:list[TagCreateSchema]
    
