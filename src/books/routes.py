from fastapi import APIRouter,status,Depends
from fastapi.exceptions import HTTPException
from src.books.schemas import Book,BookUpdate,BookCreateModel
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
import uuid
from src.auth.dependencies import AccessTokenBearer

book_router=APIRouter()
book_service=BookService()
access_token_bearer=AccessTokenBearer()

@book_router.get("/",response_model=list[Book])
async def get_all_books(session:AsyncSession=Depends(get_session),user_details=Depends(access_token_bearer))->list:
   print(user_details)
   books= await book_service.get_all_books(session)
   return books


@book_router.post("/",status_code=status.HTTP_201_CREATED,response_model=BookCreateModel)
async def create_book(book_data:BookCreateModel,session:AsyncSession=Depends(get_session),user_details=Depends(access_token_bearer))->dict:
     new_book= await book_service.create_book(book_data,session)
     return new_book

@book_router.get("/{book_uid}",response_model=Book)
async def get_book_by_id(book_uid:str,session:AsyncSession=Depends(get_session),user_details=Depends(access_token_bearer))->dict:
    try:
        book_id=uuid.UUID(book_uid)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid book UID format")

    book=await book_service.get_book_by_id(book_id,session)
    if book:
        return book
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(book_uid:str,book_update:BookUpdate,session:AsyncSession=Depends(get_session),user_details=Depends(access_token_bearer)) -> Book:
       try:
              book_id=uuid.UUID(book_uid)
       except ValueError:
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid book UID format")
       updated_book=await book_service.update_book(book_id,book_update,session)
       if updated_book:
             return updated_book
       else:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
         
@book_router.delete("/{book_uid}")
async def delete_book(book_uid:str,book_data=Book,session:AsyncSession=Depends(get_session),user_details=Depends(access_token_bearer))->dict:
     deleted_book=await book_service.delete_book(book_uid,session)
     if deleted_book:
           return {"message":"Book deleted successfully"}
     else:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


