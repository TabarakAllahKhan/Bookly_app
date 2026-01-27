from src.db.models import User, Book, Review
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import UserCreateModel,UserModel
from src.auth.utils import generate_hash_password
from sqlmodel import select
from fastapi import Depends
from src.db.main import get_session
from sqlalchemy.exc import IntegrityError
from src.errors import UserAlreadyExists



class UserService:
    '''
    This class contains the logic related to user data
    '''
    async def get_user_by_email(self,email:str,session:AsyncSession):
        statement=select(User).where(User.email==email)
        
        result=await session.exec(statement)
    
        return result.first()
    
    async def user_exists(self,email:str,session:AsyncSession)->bool:
        statement=await self.get_user_by_email(email,session)
        return True if statement else False
    
    async def create_user(self,user_data:UserCreateModel,session:AsyncSession):
       
            new_user=user_data.model_dump()
            user=User(**new_user)
            user.password_hash=generate_hash_password(new_user['password'])
            user.role="user"
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
                return user
            except IntegrityError as err:
                await session.rollback()
                msg = str(err.orig) if hasattr(err, 'orig') else str(err)
                # determine which field caused the conflict
                if 'username' in msg or 'ix_users_username' in msg or 'Key (username)' in msg:
                    raise UserAlreadyExists('User with given username already exists')
                if 'email' in msg or 'ix_users_email' in msg or 'Key (email)' in msg:
                    raise UserAlreadyExists('User with given email already exists')
                # fallback
                raise UserAlreadyExists('User with given credentials already exists')
        
    async def is_user_verified(self,email:str,session:AsyncSession):
        statement=await self.get_user_by_email(email=email,session=session)
        if statement is not None:
            return statement.is_verified
    
    async def get_verified(self,email,session:AsyncSession):
        user=await self.get_user_by_email(email=email,session=session)
        
        if not user:
            raise ValueError("User not found")
        
        if user.is_verified:
            return {"verified":True,"msg":"user is already verified"}
        
        user.is_verified=True
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "verified":True,
            "message":"user is verified"
        }
    async def delete_user(self,email:str,session:AsyncSession):
        user=await self.get_user_by_email(email=email,session=session)
        if user:
            # delete reviews authored by the user
            statement = select(Review).where(Review.user_uid == user.uid)
            result = await session.exec(statement)
            for r in result.all():
                await session.delete(r)

            # find books owned by the user
            book_stmt = select(Book).where(Book.user_uid == user.uid)
            book_res = await session.exec(book_stmt)
            books = book_res.all()

            # delete reviews for those books, then delete the books
            for b in books:
                b_rev_stmt = select(Review).where(Review.book_uid == b.id)
                b_rev_res = await session.exec(b_rev_stmt)
                for br in b_rev_res.all():
                    await session.delete(br)
                await session.delete(b)

            # finally delete the user
            await session.delete(user)
            await session.commit()
            return True
        return False
            
    async def update_user_password(self, email: str, new_password: str, session: AsyncSession):
        user = await self.get_user_by_email(email=email, session=session)
        if user:
            # hash the provided plaintext password and store it on the user
            user.password_hash = generate_hash_password(new_password)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        return None
            
            
        
        
    