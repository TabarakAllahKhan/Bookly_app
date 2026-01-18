from fastapi import APIRouter, Body
from src.db.main import get_session
from src.reviews.schema import ReviewCreateSchema
from src.reviews.review_service import ReviewService
from fastapi import Depends
from src.auth.dependencies import get_current_logged_user
from fastapi import HTTPException
from src.reviews.schema import ReviewCreateSchema
from src.db.models import User

review_service=ReviewService()
review_router=APIRouter()

@review_router.post("/add_review/{book_uid}")
async def add_review(book_uid:str,current_user=Depends(get_current_logged_user),review_data=ReviewCreateSchema,session=Depends(get_session)):
    user=current_user.email
    service=await review_service.create_review(user_email=user,book_uid=book_uid,review_data=review_data,session=session)
   
    
    if service:
        return service
    else:
        raise ValueError("value not found")
    
    