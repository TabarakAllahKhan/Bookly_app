from src.auth.user_model import User
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_hash_password
from sqlmodel import select



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
            await session.commit()
            await session.refresh(user)
            return user        
            
            
            
            
        
        
    