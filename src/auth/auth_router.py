from fastapi import APIRouter,Depends,status
from src.auth.schemas import UserCreateModel,UserModel,UserLoginModel
from src.auth.user_service import UserService
from src.db.main import get_session
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import access_token,decode_token,verify_password
from datetime import timedelta,datetime
from src.config import Config
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer,AccessTokenBearer
from src.db.redis import check_black_list, create_jti_blocklist

refresh_token_bearer=RefreshTokenBearer()

REFRESH_TOKEN_EXPIRE=Config.REFRESH_TOKEN_EXPIRE

auth_router=APIRouter()
user_service=UserService()

@auth_router.post("/signup",response_model=UserModel,status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreateModel,session:AsyncSession=Depends(get_session)):
    email=user_data.email
    user_exist= user_service.user_exists(email,session)
    if await user_exist:
       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User with this email already exists")
    else:
        user=await user_service.create_user(user_data,session)
    return user

@auth_router.post("/login",status_code=status.HTTP_200_OK)
async def login(user_login_data:UserLoginModel,session:AsyncSession=Depends(get_session)):
    '''
      1) - First it will check the user exist or not
      2) - If exist then the jwt token will be granted 
    '''
    email=user_login_data.email
    password=user_login_data.password
    
    user=await user_service.get_user_by_email(email,session)
    if user is not None:
        # check if password is valid from database
        password_valid=verify_password(password,user.password_hash)
        if password_valid:
            token=access_token(
                user_data={
                    "email":email,
                    "u_id":str(user.uid)
                }
            )
            # creating a refreash token
            refreash_token=access_token(
                user_data={
                    "email":email,
                    "u_id":str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRE)
            )
        return JSONResponse(
            content={
                "message":"Login successful",
                "access_token":token,
                "refreash_token":refreash_token,
                "user":{
                    "email":user.email,
                    "u_id":str(user.uid)
                }
                
            },
            status_code=200
            
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    
@auth_router.get("/refresh_token")
async def get_new_access_token(token_details:dict=Depends(refresh_token_bearer),session:AsyncSession=Depends(get_session)):
    '''
      This function will generate a new access token based on 
      the refresh token is provided This function will be used
      when the access token user logged in is expired and we
      want to keep user logged in
      
      ARGS:
      token_details : Accepts a token in decoded dictionary format
      session : Returns The AsyncSession 
    '''
    expiry_date=token_details['exp']
    
    if datetime.fromtimestamp(expiry_date) > datetime.now():
        new_access_token=access_token(
            user_data=token_details['user']
        )
        return JSONResponse(
            content={"access_token":new_access_token},
            status_code=status.HTTP_200_OK
            
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid or not found")

@auth_router.get("/logout")
async def revoked_token(token_details:dict=Depends(AccessTokenBearer())):
    jti=token_details['jti']
    await create_jti_blocklist(jti)
    
    return JSONResponse(
        content={
            "message":"Logged Out"
        },
        status_code=status.HTTP_200_OK
    )
    
    