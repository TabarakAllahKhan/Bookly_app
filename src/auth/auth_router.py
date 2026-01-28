from fastapi import APIRouter,Depends,status,BackgroundTasks
from src.auth.schemas import UserCreateModel,UserModel,UserLoginModel,EmailSchema,PasswordResetSchema,PasswordResetConfirmSchema
from src.auth.user_service import UserService
from src.db.main import get_session
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import access_token,decode_token,verify_password,create_email_token,decode_email_token
from datetime import timedelta,datetime
from src.config import Config
from fastapi.responses import JSONResponse
from .dependencies import RefreshTokenBearer,AccessTokenBearer,get_current_logged_user,RoleChecker
from src.db.redis_client import check_black_list, create_jti_blocklist
from redmail import gmail
import os
from pathlib import Path
from  src.celerly import send_email

BASE_DIR=Path(__file__).resolve().parent

gmail.username=Config.GMAIL
gmail.password=Config.GMAIL_PASSWORD

from src.errors import (
    UserAlreadyExists,
    UserNotFound,
    InvalidToken
)

refresh_token_bearer=RefreshTokenBearer()

REFRESH_TOKEN_EXPIRE=Config.REFRESH_TOKEN_EXPIRE

auth_router=APIRouter()
user_service=UserService()
role_checker=RoleChecker(['admin','user'])

@auth_router.post("/send_mail")
async def send_mail(emails: EmailSchema, background_tasks: BackgroundTasks):
    # Extract the list of addresses from your Pydantic model
    recipient_list = emails.addresses
    
    # Define the HTML content
    html_content = """
    <h1>Welcome to Bookly</h1>
    <p>This is a test email from the <b>Bookly</b> application. you are ready to go</p>
    """
    try:
        send_email.delay(
            subject="Test Email from Bookly",
            receivers=recipient_list,
            html=html_content,
            text="This is a test email from the Bookly application. you are ready to go"
        )
    except Exception as e:
        import logging
        logging.exception("Celery task failed, falling back to background task")
        background_tasks.add_task(
            gmail.send,
            subject="Test Email from Bookly",
            receivers=recipient_list,
            html=html_content,
            text="This is a test email from the Bookly application. you are ready to go"
        )
    
    return {"message": "Email is being sent successfully"}
    
    
@auth_router.post("/signup",response_model=UserModel,status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreateModel,background_tasks:BackgroundTasks,session:AsyncSession=Depends(get_session)):
    email=user_data.email
    user_exist = user_service.user_exists(email, session)
    if await user_exist:
        raise UserAlreadyExists()
    user = await user_service.create_user(user_data, session)

    # attempt to create verification token and send email via Celery; fallback to background task
    try:
        domain = Config.DOMAIN
        token = create_email_token({"email": email})
        verify_link = f"http://{domain}/api/v1/auth/verify/{token}"
        html_message = f"""
           <h1>Verify your email</h1>
           <p>Click this <a href="{verify_link}">link</a> to verify your email address</p>
        """
        try:
            send_email.delay(
                subject="Verify your email",
                receivers=[email],
                html=html_message,
                text=f"Verify: {verify_link}"
            )
        except Exception:
            import logging
            logging.exception("Celery task failed, falling back to background task")
            background_tasks.add_task(
                gmail.send,
                subject="Verify your email",
                receivers=[email],
                html=html_message,
                text=f"Verify: {verify_link}"
            )
    except Exception:
        import logging
        logging.exception("Failed to create verification token or schedule email")

    return {"verified": user.is_verified, "message": "User created successfully. Please verify your email."}

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
                    "u_id":str(user.uid),
                    "role":user.role
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
    raise UserNotFound()

    
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
    raise InvalidToken()


@auth_router.get("/me")
async def get_current_user(user_details=Depends(get_current_logged_user),_:bool=Depends(role_checker)):
    return user_details


@auth_router.get("/verify/{token}")
async def verify_user_email(token:str,session:AsyncSession=Depends(get_session)):
    try:
        token_data=decode_email_token(token)
        email=token_data.get("email")
        user=await user_service.get_user_by_email(email=email,session=session)
        if not user:
            raise UserNotFound()
        if user.is_verified:
            return JSONResponse(
                content={
                    "verified":True,
                    "message":"User is already verified"
                },
                status_code=status.HTTP_200_OK
            )
        else:
            get_verfied_user=await user_service.get_verified(email,session)
            return get_verfied_user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )


@auth_router.post("/getverified",response_model=UserModel)
async def get_verified(email:str,session:AsyncSession=Depends(get_session)):
    
    try:
        return await user_service.get_verified(email,session)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@auth_router.delete("/delete_user")
async def delete_user(email:str,session:AsyncSession=Depends(get_session)):
    deleted=await user_service.delete_user(email,session)
    if deleted:
        return JSONResponse(
            content={
                "message":"User deleted successfully"
            },
            status_code=status.HTTP_200_OK
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
    
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
    
@auth_router.post("/password_reset")
async def password_reset(email:PasswordResetSchema,background_tasks:BackgroundTasks,session:AsyncSession=Depends(get_session)):
      email=email.email
      user=await user_service.get_user_by_email(email,session)
      if not user:
          raise UserNotFound()
      else:
           token=create_email_token({"email":email})
           domain=Config.DOMAIN
           reset_link=f"http://{domain}/api/v1/auth/reset_password/{token}"
           html_message=f"""
                  <h1>Password Reset Request</h1>
                  <p>Click this <a href="{reset_link}"> link</a> to reset your password</p>
              """
           background_tasks.add_task(
                gmail.send,
                subject="Password Reset Request",
                receivers=[email],
                html=html_message,
            )
           return JSONResponse(
               content={
                     "message":"Password reset link has been sent to your email"
               }
               ,
               status_code=status.HTTP_200_OK
           )

@auth_router.post("/reset_password/{token}")
async def reset_confirm_password(token:str,password:PasswordResetConfirmSchema,session:AsyncSession=Depends(get_session)):
    token_data=decode_email_token(token)
    user_email=token_data.get("email")
    user_password=password.new_password
    confirm_password=password.confirm_password
    
    if user_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    if user_email is not None:
        user=await user_service.get_user_by_email(user_email,session)
        if not user:
            raise UserNotFound()
        
        await user_service.update_user_password(user_email,user_password,session)
        return JSONResponse(
            content={
                "message":"Password has been reset successfully"
            },
            status_code=status.HTTP_200_OK
        )