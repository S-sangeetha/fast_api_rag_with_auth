from pydantic import BaseModel , Field

class UserReuest(BaseModel):
    name : str
    email : str
    password:str= Field(..., min_length= 8,max_length=10)

class UserResponse(BaseModel):
    _id :str
    name:str
    email :str

class LoginRequest(BaseModel):
    email :str
    password:str 

class LoginResponse(BaseModel):
    access_token : str
    refresh_token :str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str