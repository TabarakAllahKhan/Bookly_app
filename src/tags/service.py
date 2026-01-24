from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select,desc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService
from src.db.models import Tag

from .schemas import TagAddSchema,TagCreateSchema

book_service=BookService()

server_error=HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Some thing went wrong"
)

class TagService:
    async def get_all_tags(self,session:AsyncSession):
        '''
          Returns all tags
        '''
        statement=select(Tag).order_by(desc(Tag.created_at))
        result=await session.exec(statement)
        return result.all()
    
    async def add_tag_to_books(
        self,
        book_uid:str,
        tag_data:TagAddSchema,
        session:AsyncSession
    ):
        book=await book_service.get_book_by_id(book_uid=book_uid,session=session)
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="book not found"
            )
        for tag_item in tag_data.tags:
            result=await session.exec(
                select(Tag).where(Tag.name==tag_item.name)
            )
            tag=result.one_or_none()
            if not tag:
                tag=Tag(name=tag_item.name)
            book.tags.append(tag)
            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book
    
    async def get_tag_by_uid(self,tag_uid:str,session:AsyncSession):
        statement=select(Tag).where(Tag.uid==tag_uid)
        result=await session.exec(statement)
        return result.first()
    
    async def add_tag(self,tag_data:TagCreateSchema,session:AsyncSession):
        statement=select(Tag).where(Tag.name==tag_data.name)
        result=await session.exec(statement)
        tag=result.first()
        
        if tag:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tag exist"
            )
        new_tag=Tag(name=tag_data.name)
        session.add(new_tag)
        await session.commit()
        return new_tag
    
    async def update_tag(
        self,tag_uid:str,tag_update_data:TagCreateSchema,session:AsyncSession
    ):
        tag=await self.get_tag_by_uid(tag_uid=tag_uid,session=session)
        update_data_dict=tag_update_data.model_dump()
        
        for key,value in update_data_dict.items():
            setattr(tag,key,value)
            await session.commit()
            await session.refresh(tag)
            
        return tag
    
    async def delete_tag(self,tag_uid:str,session:AsyncSession):
        tag=await self.get_tag_by_uid(tag_uid=tag_uid,session=session)
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NOT FOUND"
            )
        await session.delete(tag)
        await session.commit()
        
    