from fastapi import APIRouter, Depends
from models import booking_model
from fastapi import Request, Response
from utils.pydantic_base_models import *
from utils.utils import get_token_header
from models.booking_model import get_user_current_cart, add_trip_to_users_booking_cart, delete_trip_from_users_booking_cart

router = APIRouter(
    prefix="/api/booking",
    tags=["Booking"]
)

@router.get("/", summary="取得尚未確認下單的預定行程", tags=["Booking"])
async def get_current_cart(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return get_user_current_cart(token_data)

@router.post("/", summary="建立新的預定行程", tags=["Booking"])
async def add_trip_to_cart(booking_details: BookingFormData, request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return add_trip_to_users_booking_cart(booking_details, token_data)

@router.delete("/", summary="刪除目前的預定行程", tags=["Booking"])
async def delete_trip_from_cart(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return delete_trip_from_users_booking_cart(token_data)  
