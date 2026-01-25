from src.db.models import User
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
            await session.delete(user)
            await session.commit()
            return True
        return False
            
            
            
            
        
        
    