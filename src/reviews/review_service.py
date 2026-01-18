from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select
from src.db.models import Review
from src.books.service import BookService
from src.auth.user_service import UserService
from fastapi import Depends
from src.reviews.schema import ReviewCreateSchema

user_service=UserService()
book_service=BookService()

class ReviewService:
    async def retrive_all_reviews(self):
        pass
    
    async def get_review_by_id():
        pass
    
    async def create_review(self,user_email:str,book_uid:str,review_data:ReviewCreateSchema,session:AsyncSession):
        try:
            user=await user_service.get_user_by_email(user_email,session)
            book=await book_service.get_book_by_id(book_uid,session)
            
            if not user or not book:
                return {"message":"The user or book not found"}
            else:
                review_data_dict=review_data.model_dump()
                new_review=Review(**review_data_dict)
                new_review.user=user
                new_review.book=book
                session.add(new_review)
                await session.commit()
                await session.refresh(new_review)
                return new_review
    
        except:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The creation of review failed"
            )
        
    
    async def update_review():
        pass
    
    async def delete_review():
        pass    