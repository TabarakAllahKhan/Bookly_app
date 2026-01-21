from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select,desc
from src.db.models import Review
from src.books.service import BookService
from src.auth.user_service import UserService
from fastapi import Depends
from src.reviews.schema import ReviewCreateSchema,ReviewUpdateSchema
import uuid

user_service=UserService()
book_service=BookService()

class ReviewService:
    async def retrive_all_reviews(self,session:AsyncSession):
        get_all=select(Review).order_by(desc(Review.created_at))
        result=await session.exec(get_all)
        return result.all()
        
    
    async def get_review_by_id(self,review_id:str,session:AsyncSession):
        try:
            # ensure review_id is a UUID when querying
            if isinstance(review_id, uuid.UUID):
                rid = review_id
            else:
                try:
                    rid = uuid.UUID(review_id)
                except (ValueError, TypeError):
                    return None

            get_review = select(Review).where(Review.uid == rid)
            result = await session.exec(get_review)
            review = result.first()
            return review if review is not None else None
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The review Not Found"
            )
                
        
    
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
        
    
    async def update_review(self,review_id:str,review_data:ReviewUpdateSchema,session:AsyncSession):
             if isinstance(review_id,uuid.UUID):
                 review_uid=review_id
             else:
                 try:
                     review_uid=uuid.UUID(review_id)
                 except(ValueError,TypeError):
                     return None
             review_update=await self.get_review_by_id(review_id=review_id,session=session)
             if review_update is not None:
                 update_data=review_data.model_dump(exclude_unset=True)
                 for key,value in update_data.items():
                     setattr(review_update,key,value)
                 await session.commit()
                 return review_update
             
                     
                     
                     
                 
    
    async def delete_review(self,review_id:str,session:AsyncSession)->bool:
        review_to_delete = await self.get_review_by_id(review_id=review_id,session=session)

        if review_to_delete is not None:
            await session.delete(review_to_delete)
            await session.commit()
            return True
        else:
            return False