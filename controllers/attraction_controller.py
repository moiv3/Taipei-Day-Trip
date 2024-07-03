from fastapi import APIRouter, Request, Response
from models.attraction_model import get_attractions_by_query_string, get_attraction_by_id
from utils.pydantic_base_models import *

# weird choice, maybe needs checking
router = APIRouter(
    prefix="/api",
    tags=["Attraction"]
)

# check if we can omit response => it didn't break!
@router.get("/attractions", response_model=AttractionQueryOut, summary="取得景點資料列表", tags=["Attraction"],
         responses={400: {"model": Error}, 500: {"model": Error}})
# async def get_attractions(request: Request, response: Response, page: int, keyword: str | None = None):
async def get_attractions(request: Request, page: int, keyword: str | None = None):
    return get_attractions_by_query_string(page, keyword)

@router.get("/attraction/{attractionId}", response_model=AttractionSpecifyOut, summary="根據景點編號取得景點資料", tags=["Attraction"],
         responses={400: {"model": Error}, 500: {"model": Error}})
async def get_one_attraction(request: Request, attractionId: int):
    return get_attraction_by_id(attractionId)
