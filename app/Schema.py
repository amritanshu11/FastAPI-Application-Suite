from typing import Optional
from pydantic import BaseModel , EmailStr, conint
from datetime import datetime


class post(BaseModel):  # WE can ensure that the frontend is sending the exact data that we want using the pydantic model
    title: str
    content: str
    published: bool = True
    
    class Config:
        from_attributes = True

class userout(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    
    class Config:
        from_attributes = True
    
class postResponse(post):
    id : int
    created_at : datetime
    user_id : int
    owner : userout
    
    class Config:
        from_attributes = True

class PostOut(BaseModel):
    Post : postResponse
    Votes : int
    
    class Config:
        from_attributes = True
    
       
class user(BaseModel):
    email : EmailStr
    password : str
    

    
class UserLogin(BaseModel):
    email : EmailStr
    password : str   
    
class token(BaseModel):
    access_token : str
    token_type : str

class tokenData(BaseModel):
    id : Optional[str] = None
    
class vote(BaseModel):
    post_id : int
    dir : conint(le=1) 