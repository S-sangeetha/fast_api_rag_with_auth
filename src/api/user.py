from fastapi import APIRouter , status ,Depends
from src.models.user import UserReuest, UserResponse , LoginRequest,LoginResponse
from typing import List
from src.service.user import user_service
from src.dependencies import get_current_user


router = APIRouter(
    prefix = "/user",
    tags=["user"]
)


@router.post(
    "/create_user",
    response_model= UserResponse,
    status_code=status.HTTP_201_CREATED,
    
)

async def create_user(request : UserReuest):
    return await user_service.create_user(request)


@router.get(
    "/get_user/{id}",
     response_model= UserResponse,
     status_code=status.HTTP_200_OK,
)

async def get_user(id: str ,  current_user=Depends(get_current_user)):
    return await user_service.get_user(id)

