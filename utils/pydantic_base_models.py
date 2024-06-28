from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Annotated, Literal
from annotated_types import MinLen

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