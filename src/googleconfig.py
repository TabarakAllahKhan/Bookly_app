
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_sso.sso.google import GoogleSSO
from jose import jwt, JWTError
from datetime import datetime, timedelta
from src.config import Config

google_sso=GoogleSSO(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.CLIENT_SECRET,
    redirect_uri=Config.GOOGLE_REDIRECT_URI,
    allow_insecure_http=True
)

oauth2scheme=OAuth2PasswordBearer(tokenUrl="auth/userlogin")
