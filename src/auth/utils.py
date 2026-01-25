# This file contains utility functions for authentication.
import bcrypt
from datetime import timedelta as td
from datetime import datetime
import jwt
import uuid
from src.config import Config
from itsdangerous import URLSafeTimedSerializer
import logging

def generate_hash_password(password:str)->str:
    '''
    Docstring for generate_hash_password
    
    This function takes a plain text password as input and returns the hashed version of the password.
    It uses the passlib library to hash the password securely.
    '''
    pw_bytes = password.encode('utf-8')[:72]
    hashed_bytes = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def verify_password(password:str,hashed_password:str)->bool:
    '''
    This function verifies if the provided plain text password matches the hashed password.
    It returns True if the passwords match, otherwise False.
    '''
    pw_bytes = password.encode('utf-8')[:72]
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode('utf-8')
    else:
        hashed_bytes = hashed_password
    return bcrypt.checkpw(pw_bytes, hashed_bytes)


def access_token(user_data:dict,expiry:td=None,refresh:bool=False):
    '''
     This function generates an JWT access token for the user.
    ARGS:
        user_data (dict): A dictionary containing user information to be included in the token payload.
        expiry (timedelta): The duration for which the token will be valid.
        refresh (bool): A flag indicating whether the token is a refresh token.
    RETURNS:
        str: The generated JWT access token as a string.
    '''
    payload={}
    payload['user']=user_data
    payload['exp']=datetime.now()+ (expiry if expiry is not None else td(minutes=Config.ACCESS_TOKEN_EXPIRE))
    payload['jti']=str(uuid.uuid4())
    payload['refresh']=refresh

    token=jwt.encode(
        payload=payload,
        key=Config.SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
        
         
    )
    
    return token

def decode_token(token:str)->dict:
    '''
    This function decodes a JWT token and returns the payload as a dictionary.
    ARGS:
        token (str): The JWT token to be decoded.
    RETURNS:
        dict: The decoded payload of the JWT token.
    '''
    try:
        payload=jwt.decode(
            jwt=token,
            key=Config.SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
    

serializer=URLSafeTimedSerializer(Config.SECRET_KEY,salt="email-configration")

def create_email_token(data:dict):
    """This function creates a time-sensitive email token using itsdangerous library.

    Args:
        data (dict): The data to be included in the token.
    """
    
    token=serializer.dumps(data)
    return token

def decode_email_token(token:str)->dict:
    try:
        email_token_data=serializer.loads(token)
        return email_token_data
    except Exception as e:
        logging.error(f"Error decoding email token: {e}")

        raise Exception("Invalid or expired email token")
    
