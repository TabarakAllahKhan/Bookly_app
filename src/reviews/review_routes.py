from fastapi import APIRouter, Body
from src.db.main import get_session
from src.reviews.schema import ReviewCreateSchema,ReviewGetSchema
from src.reviews.review_service import ReviewService
from fastapi import Depends
from src.auth.dependencies import get_current_logged_user
from fastapi import HTTPException
from src.reviews.schema import ReviewCreateSchema,ReviewUpdateSchema
from src.db.models import User

review_service=ReviewService()
review_router=APIRouter()

@review_router.get("/get_all_reviews")
async def get_all_reviews(session=Depends(get_session)):
    get_reviews=await review_service.retrive_all_reviews(session=session)
    return get_reviews

@review_router.get("/get_review_by_id/{review_id}")
async def get_review_by_id(review_id:str,session=Depends(get_session)):
    get_review=await review_service.get_review_by_id(review_id=review_id,session=session)
    return get_review

@review_router.post("/add_review/{book_uid}",status_code=200)
async def add_review(
book_uid:str,
review_data:ReviewCreateSchema=Body(...),
current_user=Depends(get_current_logged_user),
session=Depends(get_session)                                   
):
    user_email=current_user.email
    
    new_review=await review_service.create_review(user_email=user_email,book_uid=book_uid,review_data=review_data,session=session)
    
    return new_review
    
@review_router.delete("/delete_review/{review_id}")
async def delete_user_review(review_id:str,session=Depends(get_session)):
    delete_review= await review_service.delete_review(review_id=review_id,session=session)
    return delete_review

@review_router.patch("/update_review/{review_id}")
async def update_user_review(review_id:str,review_data:ReviewUpdateSchema=Body(...),session=Depends(get_session)):
    updated_data=await review_service.update_review(review_id=review_id,review_data=review_data,session=session)
    return updated_data
