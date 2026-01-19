# This file contains the logic for crud operations on the Book model.
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreateModel,BookUpdate
from sqlmodel import select,desc
from src.db.models import Book
from fastapi.exceptions import HTTPException
from fastapi import status
import uuid

class BookService:
    '''This BookService class contains methods for CRUD operations on the Book model.
       When a method is called, it interacts with the database using the provided session.
    '''
    async def get_all_books(self,session:AsyncSession):
        '''This method retrives all books from the database.
           It returns a list of Book objects.
        '''
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def get_user_book_submission(self,u_id:str,session:AsyncSession):
        statement=select(Book).where(Book.user_uid==u_id)
        result=await session.exec(statement)
        books=result.all()
        return books if books is not None else None
    
    async def get_book_by_id(self,book_uid,session:AsyncSession):
        '''This method retrieves a book by its unique identifier (uid).
           It returns a Book object if found, otherwise None.
        '''
        try:
         statement = select(Book).where(Book.id == book_uid)
         result = await session.exec(statement)
         book=result.first()
         return book if book is not None else None
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
    async def create_book(self,book_data:BookCreateModel,user_uid:str,session:AsyncSession):
          book_data_dict=book_data.model_dump()
          new_book=Book(**book_data_dict)
          new_book.user_uid=user_uid
          session.add(new_book)
          await session.commit()
          await session.refresh(new_book)
          return new_book
          
    async def update_book(self,book_uid,update_data:BookUpdate,session:AsyncSession):
            if isinstance(book_uid, uuid.UUID):
                book_id = book_uid
            else:
                try:
                    book_id = uuid.UUID(book_uid)
                except (ValueError, TypeError):
                    return None
            book_to_update= await self.get_book_by_id(book_id,session)
            if book_to_update is not None:
             update_data_dict=update_data.model_dump(exclude_unset=True)
             for key,value in update_data_dict.items():
                setattr(book_to_update,key,value)
             await session.commit()
             return book_to_update
            else:
                return None
            
              
                
    async def delete_book(self,book_uid:str,session:AsyncSession):
          book_to_delete= await self.get_book_by_id(book_uid,session)
          if book_to_delete is not None:
                await session.delete(book_to_delete)
                await session.commit()
                return True
          else:
                return False

