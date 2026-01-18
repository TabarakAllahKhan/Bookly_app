from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Request, status,Depends
from fastapi.exceptions import HTTPException
from .utils import decode_token
from src.db.redis import check_black_list
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.user_service import UserService
from src.db.models import User

user_service=UserService()

class TokenBearer(HTTPBearer):
    '''
        This Class functions is used for jwt auth.
        FUNCTIONALITIES:
        1- Check the Header structure that if JWT is Present and Auth method is Bearer
        2- Extract the user details from the Header
        3- Check if user details are missing or not
        4- Decode the token
        5- Check the JWT ID in redis blacklist
        6- Checks weather the token is access or refreash
    '''
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds: HTTPAuthorizationCredentials | None = await super().__call__(request)

        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization credentials missing",
            )

        token = creds.credentials
        token_data = decode_token(token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        if await check_black_list(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error":"This token is been revoked","resolution":"Plz get new token"}
            )
        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please override this method in child classes")

class AccessTokenBearer(TokenBearer):
    '''
    Docstring for AccessTokenBearer
    
    This class will be used in book routes as the access
    token will be used in book routes we cant allow to use
    refresh tokens so access token will be checked here to 
    ensure that access token is present while accessing the
    book apis
    '''
    def verify_token_data(self, token_data: dict) -> None:
        if token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid access token",
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a valid refresh token",
            )


       
async def get_current_logged_user(user_details:dict=Depends(AccessTokenBearer()),session:AsyncSession=Depends(get_session)):
        '''
        This function is used in role base access control to get the current logged in user
        in our app
        
        ROLE :
        This function will be used by admin
        '''
        # extracting the user email from user dictionary
        
        user_email=user_details['user']['email']
        user=await user_service.get_user_by_email(user_email,session)
        if user is not None:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
        
        
# creating a role checking dependency
class RoleChecker:
    def __init__(self,allowed_role:list[str])->None:
        self.allowed_role=allowed_role
    
    def __call__(self,current_user:User=Depends(get_current_logged_user)):
        
        if current_user.role in self.allowed_role:
            return True
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Access Denied")

async def get_google_user(req:Request):
    try:
        async with google_sso:
            user=await google_sso.verify_and_process(request=req)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google login failed"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"authentication failed {str(e)}"
        )