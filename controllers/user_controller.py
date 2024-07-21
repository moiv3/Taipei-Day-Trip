from fastapi import APIRouter, Request, Response, Depends
from utils.pydantic_base_models import *
from models.user_model import create_user, authenticate_user, check_user_signin_status
from utils.utils import get_token_header

router = APIRouter(
    prefix="/api/user",
    tags=["User"]
)

@router.post("/", summary="註冊一個新的會員")
async def signup(sign_up_credentials: SignupFormData, request: Request, response: Response):
    return create_user(email=sign_up_credentials.email, password=sign_up_credentials.password, name=sign_up_credentials.name) 

@router.put("/auth", response_model=TokenOut, summary="登入會員帳戶")
async def signin(sign_in_credentials: SigninFormData, request: Request, response: Response):
    return authenticate_user(email=sign_in_credentials.email, password=sign_in_credentials.password)

# check sign in status(predicted usage: on every page). response model integration was helped by ChatGPT
@router.get("/auth", response_model=UserSigninDataOut, summary="取得當前登入的會員資訊", tags=["User"])
async def check_signin_status(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return check_user_signin_status(token_data)