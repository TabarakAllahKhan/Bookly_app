from fastapi import FastAPI,Header
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
     name:str
     age:int
     address:Optional[str]=None


app=FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/greet/{name}")
async def greet_name(name:str)->dict:
    '''This endpoint generates a greeting message for the 
       dynamic name provided in the URL path.
         Args:
            name (str): The name to include in the greeting message.
            Returns:
            dict: A dictionary containing the greeting message.
    '''
    return {"greeting":f"Hello, {name}!"}

@app.get("/greet_me")
async def greet_me(name:str)->dict:
    '''This endpoint generates a greeting message for the 
       name provided as a query parameter.
         Args:
            name (str): The name to include in the greeting message.
            Returns:
            dict: A dictionary containing the greeting message.
    '''
    return {"greeting":f"Hello, {name}!"}

@app.get("/sayhi")
async def sayhi(name:Optional[str]="user",age:int=0)->dict:
        '''
        This endpoint is a mix of path and query parameters.
        It generates a greeting message that includes both the name
        and age provided by the user.
        Args:
            name (str): The name to include in the greeting message.
            age (int): The age to include in the greeting message.
        Returns:
            dict: A dictionary containing the greeting message.
        '''
        return {"message":f"Hi,{name}! You are {age} years old."}

@app.post("/create_user")
async def create_user(user:User):
     return user

@app.get("/getheader")
async def get_header(
     accept:str=Header(None),
     content_type:str=Header(None),
     user_agent:str=Header(None),
     host:str=Header(None)
     ):
     request_headers={}
     request_headers["Accept"]=accept
     request_headers["Content_Type"]=content_type
     request_headers["User_Agent"]=user_agent
     request_headers["Host"]=host
     return request_headers


if __name__=="__main__":
     import uvicorn
     uvicorn.run(app,host="0.0.0.0",port=8000)