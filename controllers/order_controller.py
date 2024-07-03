from fastapi import APIRouter, Depends
from fastapi import Request, Response
from utils.pydantic_base_models import *
from utils.utils import get_token_header
from models.order_model import get_order_by_order_number, place_order_and_process_payment


router = APIRouter(
    prefix="/api",
    tags=["Order"]
)

@router.post("/orders", response_model=PlaceOrderResponse, summary="建立新的訂單，並完成付款程序")
async def place_order(request: Request, response: Response, OrderFormData: OrderFormData, token_data: TokenOut = Depends(get_token_header)):
    return place_order_and_process_payment(OrderFormData, token_data)


@router.get("/order/{orderNumber}", response_model=GetOrderResponse, summary="根據訂單編號取得訂單資訊")
async def get_order(request: Request, response: Response, orderNumber: str, token_data: TokenOut = Depends(get_token_header)):
    return get_order_by_order_number(orderNumber, token_data)