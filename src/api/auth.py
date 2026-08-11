from fastapi import APIRouter ,status , Depends
from src.models.user import RefreshTokenRequest
from src.service.auth import auth_service
from src.models.user import UserReuest, UserResponse , LoginRequest,LoginResponse
from src.service.user import user_service
from fastapi.security import OAuth2PasswordRequestForm

router =APIRouter(
    prefix="/auth",
    tags =["Authenticaton"]
)



@router.post("/refresh")
async def refresh(request: RefreshTokenRequest):
    return await auth_service.refresh_token(request)

@router.post(
    "/login",
    response_model = LoginResponse ,
    status_code=status.HTTP_200_OK,
)
async def login(  form_data: OAuth2PasswordRequestForm = Depends() ):
    request = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )
    return await user_service.login(request)