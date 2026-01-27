from typing import Any,Callable,Optional
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI,status
class BooklyException(Exception):
    """This is the base class for all bookly errors"""
    pass

class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""
    pass

class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""
    pass

class AccessTokenRequired(BooklyException):
    """User has provided a refresh token when an access token is needed"""
    pass

class RefreshTokenRequired(BooklyException):
    """User has provided an access token when a refresh token is needed"""
    pass

class UserAlreadyExists(BooklyException):
    """User has provided an email for a user who exists during sign up."""
    def __init__(self, message: Optional[str] = None):
        self.message = message or "User with given email already exists"
        super().__init__(self.message)

class InvalidCredentials(BooklyException):
    """User has provided wrong email or password during log in."""
    pass

class InsufficientPermission(BooklyException):
    """User does not have the necessary permissions to perform an action."""
    pass

class BookNotFound(BooklyException):
    """Book Not found"""
    pass

class BookInsertionError(BooklyException):
    """Error occurred while inserting a book"""
    pass
class TagNotFound(BooklyException):
    """Tag Not found"""
    pass

class TagAlreadyExists(BooklyException):
    """Tag already exists"""
    pass

class UserNotFound(BooklyException):
    """User Not found"""
    pass

class InvalidCredentials(BooklyException):
    """User provided wrong email or password during log in."""
    pass

class AccountNotVerified(BooklyException):
    """User account is not verified."""
    pass

def create_exception_handeler(status_code:int,detail:Any)->Callable[[Request,Exception],JSONResponse]:
    
    async def exception_handeler(request:Request,exc:BooklyException)->JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"detail":detail}
        )
    return exception_handeler


def register_exception_handler(app:FastAPI):
    async def _user_already_exists_handler(request: Request, exc: UserAlreadyExists) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"error": exc.message})

    app.add_exception_handler(UserAlreadyExists, _user_already_exists_handler)
    
    app.add_exception_handler(
        UserNotFound,
        create_exception_handeler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error":"User with given id not found"
            },
        ),
    )
    
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handeler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error":"Invalid email or password"}
        )
    )
    
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handeler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error":"You do not have permission to perform this action"}
        )
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handeler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error":"Access token is required to access this resource"}
        )
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handeler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error":"Refresh token is required to access this resource"}
        )
    )
    app.add_exception_handler(
        BookNotFound,
        create_exception_handeler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error":"Book with given id not found"}
        )
    )
    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handeler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error":"Tag with given name already exists"}
        )
    )
    app.add_exception_handler(
        TagNotFound,
        create_exception_handeler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error":"Tag with given id not found"}
        )
    )
    app.add_exception_handler(
        BookInsertionError,
        create_exception_handeler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error":"An error occurred while inserting the book"}
        )
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handeler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error":"The provided token is invalid or expired"}
        )
    )
    
    app.add_exception_handler(
        RevokedToken,
        create_exception_handeler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error":"The provided token has been revoked"}
        )
    )
    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handeler(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error":"User account is not verified"}
        )
    )
    
    