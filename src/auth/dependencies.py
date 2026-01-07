from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from .utils import decode_token
from src.db.redis import check_black_list


class TokenBearer(HTTPBearer):
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