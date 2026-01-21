from pydantic import BaseModel,Field
from typing import Optional
import uuid
from datetime import datetime

class ReviewGetSchema(BaseModel):
    '''
      This class is the schema for review data
      all the icoming data will be validated using this schema
    '''
    uid:uuid.UUID
    rating:int=Field(lt=5)
    review_txt:str
    user_uid:Optional[uuid.UUID]
    book_uid:Optional[uuid.UUID]
    created_at:datetime
    updated_at:datetime
    

class ReviewCreateSchema(BaseModel):
    '''
    Docstring for ReviewCreateSchema
    
    When review data will be sent to database the sending data will be validated
    using this schema
    '''
    rating:int=Field(lt=5)
    # accept incoming JSON field `review_text` and map it to `review_txt`
    review_txt:str = Field(alias="review_text")

class ReviewUpdateSchema(BaseModel):
  rating:Optional[int]
  review_txt:Optional[str]=Field(alias="review_text")
  