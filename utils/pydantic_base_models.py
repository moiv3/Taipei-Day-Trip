from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Annotated, Literal
from annotated_types import Len, MinLen

class Error(BaseModel):
    error: bool
    message: str

class SignupFormData(BaseModel):
    name: Annotated[str, MinLen(1)]
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class SigninFormData(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class TokenOut(BaseModel):
    token: str

class UserSigninData(BaseModel):
    id: int
    name: Annotated[str, MinLen(1)]
    email: EmailStr

class UserSigninDataOut(BaseModel):
    data: UserSigninData

class Attraction(BaseModel):
    id: int
    name: str
    category: str
    description: str
    address: str
    transport: str
    mrt: str | None
    lat: float
    lng: float
    images: list[str]

class AttractionQueryOut(BaseModel):
    nextPage: int | None
    data: list[Attraction]

class AttractionSpecifyOut(BaseModel):
    data: Attraction

class BookingFormData(BaseModel):
    attractionId: int
    date: date
    time: Literal["morning", "afternoon"]
    price: int

class AttractionData(BaseModel):
    id: int 
    name: Annotated[str, MinLen(1)]
    address: Annotated[str, MinLen(1)]
    image: Annotated[str, MinLen(1)]

class ContactData(BaseModel):
    name: Annotated[str, MinLen(1)]
    email: EmailStr
    phone: Annotated[str, MinLen(1)]

class TripData(BaseModel):
    attraction: AttractionData
    date: date
    time: Literal["morning", "afternoon"]

class OrderData(BaseModel):
    price: Literal[2000, 2500] # for future complicated prices, need to adjust this line
    trip: TripData
    contact: ContactData

class OrderFormData(BaseModel):
    prime: str # On prime length, TapPay spec says 71, but is actually 64, and the test prime is 69... leave as str for now
    order: OrderData

class TappayResponse(BaseModel):
    status: int
    message: str

class PlaceOrderData(BaseModel):
    number: str
    payment: TappayResponse

class PlaceOrderResponse(BaseModel):
    data: PlaceOrderData

class GetOrderData(OrderData):
    number: str
    status: int

class GetOrderResponse(BaseModel):
    data: None | GetOrderData